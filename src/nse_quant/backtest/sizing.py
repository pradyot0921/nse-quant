"""Turn rebalance entry intents into affordable execution requests."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal, ROUND_FLOOR

from nse_quant.backtest.data import DailyBars
from nse_quant.backtest.execution import (
    ExecutionFillRequest,
    build_portfolio_fills_with_costs,
)
from nse_quant.backtest.portfolio import (
    BacktestAccountingError,
    FillSide,
    PortfolioState,
)
from nse_quant.backtest.rebalance import RebalancePlan


class OrderSizingError(RuntimeError):
    """Raised when rebalance orders cannot be sized deterministically."""


@dataclass(frozen=True)
class SizedRebalanceOrders:
    execution_date: date
    requests: tuple[ExecutionFillRequest, ...]
    skipped_entries: tuple[str, ...] = ()


def size_rebalance_orders(
    *,
    plan: RebalancePlan,
    current_state: PortfolioState,
    execution_bars: DailyBars,
    max_positions: int,
    slippage_rate: Decimal | str | int = Decimal("0.0005"),
) -> SizedRebalanceOrders:
    """Create whole-share fill requests that the portfolio can afford."""

    if execution_bars.trade_date <= plan.signal_date:
        raise OrderSizingError("execution date must be after signal date")
    if isinstance(max_positions, bool) or not isinstance(max_positions, int):
        raise TypeError("max_positions must be an integer")
    if max_positions <= 0:
        raise ValueError("max_positions must be positive")
    if len(plan.desired_symbols) > max_positions:
        raise OrderSizingError("desired symbols exceed max_positions")

    exit_requests = _exit_requests(plan, execution_bars)
    entry_requests, skipped = _entry_requests(
        plan=plan,
        current_state=current_state,
        execution_bars=execution_bars,
        exit_requests=exit_requests,
    )
    requests = tuple(exit_requests + entry_requests)

    affordable, skipped_after_costs = _reduce_until_affordable(
        requests=requests,
        current_state=current_state,
        slippage_rate=slippage_rate,
    )

    return SizedRebalanceOrders(
        execution_date=execution_bars.trade_date,
        requests=affordable,
        skipped_entries=tuple(dict.fromkeys((*skipped, *skipped_after_costs))),
    )


def _exit_requests(
    plan: RebalancePlan, execution_bars: DailyBars
) -> list[ExecutionFillRequest]:
    requests: list[ExecutionFillRequest] = []
    for order in plan.exit_orders:
        if order.quantity is None:
            raise OrderSizingError(f"exit order for {order.symbol} has no quantity")
        requests.append(
            ExecutionFillRequest(
                trade_date=execution_bars.trade_date,
                sequence=order.sequence,
                symbol=order.symbol,
                side=FillSide.SELL,
                quantity=order.quantity,
                reference_price=execution_bars.require(order.symbol).adjusted_open,
            )
        )
    return requests


def _entry_requests(
    *,
    plan: RebalancePlan,
    current_state: PortfolioState,
    execution_bars: DailyBars,
    exit_requests: list[ExecutionFillRequest],
) -> tuple[list[ExecutionFillRequest], list[str]]:
    entry_orders = plan.entry_orders
    if not entry_orders:
        return [], []

    cash_after_exits = current_state.cash + sum(
        (
            request.reference_price * Decimal(request.quantity)
            for request in exit_requests
        ),
        Decimal("0"),
    )
    target_budget = _target_entry_budget(
        plan=plan,
        current_state=current_state,
        execution_bars=execution_bars,
    )
    per_entry_budget = min(cash_after_exits / Decimal(len(entry_orders)), target_budget)

    requests: list[ExecutionFillRequest] = []
    skipped: list[str] = []
    for order in entry_orders:
        price = execution_bars.require(order.symbol).adjusted_open
        quantity = _whole_shares(per_entry_budget, price)
        if quantity <= 0:
            skipped.append(order.symbol)
            continue
        requests.append(
            ExecutionFillRequest(
                trade_date=execution_bars.trade_date,
                sequence=order.sequence,
                symbol=order.symbol,
                side=FillSide.BUY,
                quantity=quantity,
                reference_price=price,
            )
        )
    return requests, skipped


def _reduce_until_affordable(
    *,
    requests: tuple[ExecutionFillRequest, ...],
    current_state: PortfolioState,
    slippage_rate: Decimal | str | int,
) -> tuple[tuple[ExecutionFillRequest, ...], tuple[str, ...]]:
    working = list(requests)
    skipped: list[str] = []

    while True:
        try:
            fills = build_portfolio_fills_with_costs(
                working,
                slippage_rate=slippage_rate,
            ).portfolio_fills
            current_state.apply_fills(fills)
            return tuple(working), tuple(skipped)
        except BacktestAccountingError as exc:
            buy_index = _last_buy_index(working)
            if buy_index is None:
                raise OrderSizingError(str(exc)) from exc

            request = working[buy_index]
            next_quantity = request.quantity - 1
            if next_quantity <= 0:
                skipped.append(request.symbol)
                del working[buy_index]
            else:
                working[buy_index] = replace(request, quantity=next_quantity)


def _last_buy_index(requests: list[ExecutionFillRequest]) -> int | None:
    for index in range(len(requests) - 1, -1, -1):
        if requests[index].side is FillSide.BUY:
            return index
    return None


def _whole_shares(budget: Decimal, price: Decimal) -> int:
    return int((budget / price).to_integral_value(rounding=ROUND_FLOOR))


def _target_entry_budget(
    *,
    plan: RebalancePlan,
    current_state: PortfolioState,
    execution_bars: DailyBars,
) -> Decimal:
    if not plan.desired_symbols:
        return Decimal("0")

    reference_nav = current_state.cash + sum(
        (
            execution_bars.require(position.symbol).adjusted_open
            * Decimal(position.quantity)
            for position in current_state.positions
        ),
        Decimal("0"),
    )
    return reference_nav / Decimal(len(plan.desired_symbols))
