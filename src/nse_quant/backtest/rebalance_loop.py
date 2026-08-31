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
from nse_quant.backtest.portfolio import PortfolioSnapshot, PortfolioState
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
) -> RebalanceLoopResult:
    """Execute each close(T) rebalance intent at the next session open."""

    days = tuple(sorted(daily_bars, key=lambda item: item.trade_date))
    if not days:
        raise RebalanceLoopError("daily_bars is empty")
    _validate_unique_days(days)

    signals = dict(desired_symbols_by_signal_date)
    session_dates = {day.trade_date for day in days}
    unknown_signal_dates = sorted(set(signals) - session_dates)
    if unknown_signal_dates:
        raise RebalanceLoopError(
            f"signals scheduled for non-session dates: {unknown_signal_dates}"
        )

    state = starting_state
    snapshots: list[PortfolioSnapshot] = []
    executions: list[RebalanceExecution] = []

    for index, day in enumerate(days):
        if index > 0:
            previous_day = days[index - 1]
            desired_symbols = signals.get(previous_day.trade_date)
            if desired_symbols is not None:
                execution = _execute_signal(
                    signal_date=previous_day.trade_date,
                    desired_symbols=desired_symbols,
                    current_state=state,
                    execution_bars=day,
                    max_positions=max_positions,
                    slippage_rate=slippage_rate,
                )
                state = state.apply_fills(execution.costs.portfolio_fills)
                executions.append(execution)

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
        ),
    )


def _execute_signal(
    *,
    signal_date: date,
    desired_symbols: Iterable[str],
    current_state: PortfolioState,
    execution_bars: DailyBars,
    max_positions: int,
    slippage_rate: Decimal | str | int,
) -> RebalanceExecution:
    plan = plan_rebalance_orders(
        signal_date=signal_date,
        current_state=current_state,
        desired_symbols=desired_symbols,
    )
    sized_orders = size_rebalance_orders(
        plan=plan,
        current_state=current_state,
        execution_bars=execution_bars,
        max_positions=max_positions,
        slippage_rate=slippage_rate,
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
