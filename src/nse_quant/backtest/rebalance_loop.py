"""Run precomputed rebalance intents through sizing, execution, and NAV."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, Mapping

from nse_quant.backtest.data import DailyBars
from nse_quant.backtest.execution import (
    ExecutionCostResult,
    build_portfolio_fills_with_costs,
)
from nse_quant.backtest.portfolio import FillSide, PortfolioSnapshot, PortfolioState
from nse_quant.backtest.rebalance import RebalancePlan, plan_rebalance_orders
from nse_quant.backtest.sizing import SizedRebalanceOrders, size_rebalance_orders


class RebalanceLoopError(RuntimeError):
    """Raised when a rebalance schedule cannot be run deterministically."""


@dataclass(frozen=True)
class RebalanceExecution:
    signal_date: date
    execution_date: date
    plan: RebalancePlan
    sized_orders: SizedRebalanceOrders
    costs: ExecutionCostResult
    unfilled_exit_symbols: tuple[str, ...] = ()


@dataclass(frozen=True)
class RebalanceLoopResult:
    starting_state: PortfolioState
    ending_state: PortfolioState
    snapshots: tuple[PortfolioSnapshot, ...]
    executions: tuple[RebalanceExecution, ...]
    unexecuted_signal_dates: tuple[date, ...] = ()

    @property
    def final_snapshot(self) -> PortfolioSnapshot:
        if not self.snapshots:
            raise RebalanceLoopError("rebalance loop produced no daily snapshots")
        return self.snapshots[-1]


def run_rebalance_loop(
    daily_bars: Iterable[DailyBars],
    *,
    starting_state: PortfolioState,
    desired_symbols_by_signal_date: Mapping[date, Iterable[str]],
    max_positions: int,
    slippage_rate: Decimal | str | int = Decimal("0.0005"),
    target_exposure_by_signal_date: Mapping[date, Decimal | str | int] | None = None,
    untradeable_symbols_by_date: Mapping[date, Iterable[str]] | None = None,
) -> RebalanceLoopResult:
    """Execute each close(T) rebalance intent at the next session open."""

    days = tuple(sorted(daily_bars, key=lambda item: item.trade_date))
    if not days:
        raise RebalanceLoopError("daily_bars is empty")
    _validate_unique_days(days)

    signals = dict(desired_symbols_by_signal_date)
    target_exposures = _target_exposures(target_exposure_by_signal_date)
    session_dates = {day.trade_date for day in days}
    unknown_signal_dates = sorted(set(signals) - session_dates)
    if unknown_signal_dates:
        raise RebalanceLoopError(
            f"signals scheduled for non-session dates: {unknown_signal_dates}"
        )
    unknown_exposure_dates = sorted(set(target_exposures) - session_dates)
    if unknown_exposure_dates:
        raise RebalanceLoopError(
            f"target exposures scheduled for non-session dates: {unknown_exposure_dates}"
        )
    exposures_without_signals = sorted(set(target_exposures) - set(signals))
    if exposures_without_signals:
        raise RebalanceLoopError(
            f"target exposures scheduled without signals: {exposures_without_signals}"
        )
    untradeable = _untradeable_by_date(untradeable_symbols_by_date)
    unknown_untradeable_dates = sorted(set(untradeable) - session_dates)
    if unknown_untradeable_dates:
        raise RebalanceLoopError(
            f"untradeable symbols specified for non-session dates: {unknown_untradeable_dates}"
        )

    state = starting_state
    snapshots: list[PortfolioSnapshot] = []
    executions: list[RebalanceExecution] = []
    pending_signal: tuple[date, tuple[str, ...], Decimal | None] | None = None

    for index, day in enumerate(days):
        if index > 0:
            previous_day = days[index - 1]
            next_signal = signals.get(previous_day.trade_date)
            if pending_signal is not None and next_signal is not None:
                raise RebalanceLoopError(
                    "new signal arrived while prior exit is pending"
                )

            if pending_signal is not None:
                signal_date, desired_symbols, target_exposure = pending_signal
            elif next_signal is not None:
                signal_date = previous_day.trade_date
                desired_symbols = tuple(next_signal)
                target_exposure = target_exposures.get(signal_date)
            else:
                signal_date = None
                desired_symbols = None
                target_exposure = None

            if signal_date is not None and desired_symbols is not None:
                execution = _execute_signal(
                    signal_date=signal_date,
                    desired_symbols=desired_symbols,
                    target_exposure=target_exposure,
                    current_state=state,
                    execution_bars=day,
                    max_positions=max_positions,
                    slippage_rate=slippage_rate,
                    untradeable_symbols=untradeable.get(day.trade_date, ()),
                )
                state = state.apply_fills(execution.costs.portfolio_fills)
                executions.append(execution)
                pending_signal = (
                    (signal_date, tuple(desired_symbols), target_exposure)
                    if execution.unfilled_exit_symbols
                    else None
                )

        snapshots.append(state.mark_to_market(day.trade_date, day))

    return RebalanceLoopResult(
        starting_state=starting_state,
        ending_state=state,
        snapshots=tuple(snapshots),
        executions=tuple(executions),
        unexecuted_signal_dates=tuple(
            signal_date
            for signal_date in sorted(signals)
            if signal_date == days[-1].trade_date
        )
        + (() if pending_signal is None else (pending_signal[0],)),
    )


def _execute_signal(
    *,
    signal_date: date,
    desired_symbols: Iterable[str],
    target_exposure: Decimal | None,
    current_state: PortfolioState,
    execution_bars: DailyBars,
    max_positions: int,
    slippage_rate: Decimal | str | int,
    untradeable_symbols: Iterable[str] = (),
) -> RebalanceExecution:
    plan = plan_rebalance_orders(
        signal_date=signal_date,
        current_state=current_state,
        desired_symbols=desired_symbols,
        target_exposure=target_exposure,
    )
    unfilled_exit_symbols = _unfilled_exit_symbols(
        plan,
        current_state=current_state,
        execution_bars=execution_bars,
        untradeable_symbols=untradeable_symbols,
    )
    executable_plan = _executable_plan(plan, unfilled_exit_symbols)
    sized_orders = size_rebalance_orders(
        plan=executable_plan,
        current_state=current_state,
        execution_bars=execution_bars,
        max_positions=max_positions,
        slippage_rate=slippage_rate,
        blocked_sell_symbols=unfilled_exit_symbols,
        suppress_buys=bool(unfilled_exit_symbols),
    )
    costs = build_portfolio_fills_with_costs(
        sized_orders.requests,
        slippage_rate=slippage_rate,
    )
    return RebalanceExecution(
        signal_date=signal_date,
        execution_date=execution_bars.trade_date,
        plan=plan,
        sized_orders=sized_orders,
        costs=costs,
        unfilled_exit_symbols=unfilled_exit_symbols,
    )


def _validate_unique_days(days: tuple[DailyBars, ...]) -> None:
    seen: set[date] = set()
    duplicates = []
    for day in days:
        if day.trade_date in seen:
            duplicates.append(day.trade_date)
        seen.add(day.trade_date)
    if duplicates:
        raise RebalanceLoopError(f"duplicate backtest days: {duplicates}")


def _untradeable_by_date(
    values: Mapping[date, Iterable[str]] | None,
) -> dict[date, tuple[str, ...]]:
    if values is None:
        return {}
    return {trade_date: _symbols(symbols) for trade_date, symbols in values.items()}


def _unfilled_exit_symbols(
    plan: RebalancePlan,
    *,
    current_state: PortfolioState,
    execution_bars: DailyBars,
    untradeable_symbols: Iterable[str],
) -> tuple[str, ...]:
    blocked = set(_symbols(untradeable_symbols))
    exits = [order.symbol for order in plan.exit_orders if order.symbol in blocked]
    reductions = [
        symbol
        for symbol in _target_reduction_symbols(
            plan=plan,
            current_state=current_state,
            execution_bars=execution_bars,
        )
        if symbol in blocked
    ]
    return tuple(dict.fromkeys((*exits, *reductions)))


def _target_reduction_symbols(
    *,
    plan: RebalancePlan,
    current_state: PortfolioState,
    execution_bars: DailyBars,
) -> tuple[str, ...]:
    if plan.target_exposure is None or not plan.desired_symbols:
        return ()
    positions = current_state.positions_by_symbol
    reference_nav = current_state.cash + sum(
        (
            execution_bars.require(position.symbol).adjusted_open
            * Decimal(position.quantity)
            for position in current_state.positions
        ),
        Decimal("0"),
    )
    target_per_symbol = (
        reference_nav * plan.target_exposure / Decimal(len(plan.desired_symbols))
    )
    reductions = []
    for symbol in plan.desired_symbols:
        position = positions.get(symbol)
        if position is None:
            continue
        price = execution_bars.require(symbol).adjusted_open
        current_value = price * Decimal(position.quantity)
        sell_quantity = int((current_value - target_per_symbol) / price)
        if sell_quantity > 0:
            reductions.append(symbol)
    return tuple(reductions)


def _executable_plan(
    plan: RebalancePlan, unfilled_exit_symbols: tuple[str, ...]
) -> RebalancePlan:
    if not unfilled_exit_symbols:
        return plan

    blocked = set(unfilled_exit_symbols)
    return RebalancePlan(
        signal_date=plan.signal_date,
        desired_symbols=plan.desired_symbols,
        orders=tuple(
            order
            for order in plan.orders
            if order.side is FillSide.SELL and order.symbol not in blocked
        ),
    )


def _symbols(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(_symbol(value) for value in values)


def _symbol(value: str) -> str:
    symbol = value.strip().upper() if isinstance(value, str) else ""
    if not symbol:
        raise ValueError("symbol must be non-blank")
    return symbol


def _target_exposures(
    values: Mapping[date, Decimal | str | int] | None,
) -> dict[date, Decimal]:
    if values is None:
        return {}
    exposures = {}
    for signal_date, value in values.items():
        if not isinstance(signal_date, date):
            raise TypeError("target exposure dates must be dates")
        if isinstance(value, float):
            raise TypeError("target exposure must not be a binary float")
        exposure = value if isinstance(value, Decimal) else Decimal(value)
        if exposure < Decimal("0") or exposure > Decimal("1"):
            raise ValueError("target exposure must be between 0 and 1")
        exposures[signal_date] = exposure
    return exposures
