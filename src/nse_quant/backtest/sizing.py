"""Turn rebalance entry intents into affordable execution requests."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal, ROUND_FLOOR
from typing import Iterable

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
    blocked_sell_symbols: Iterable[str] = (),
    suppress_buys: bool = False,
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

    blocked = {_symbol(symbol) for symbol in blocked_sell_symbols}
    if plan.target_exposure is None:
        exit_requests = [
            request
            for request in _exit_requests(plan, execution_bars)
            if request.symbol not in blocked
        ]
        entry_requests, skipped = _entry_requests(
            plan=plan,
            current_state=current_state,
            execution_bars=execution_bars,
            exit_requests=exit_requests,
            suppress_buys=suppress_buys,
        )
        requests = tuple(exit_requests + entry_requests)
    else:
        requests, skipped = _target_exposure_requests(
            plan=plan,
            current_state=current_state,
            execution_bars=execution_bars,
            blocked_sell_symbols=blocked,
            suppress_buys=suppress_buys,
        )

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
    suppress_buys: bool = False,
) -> tuple[list[ExecutionFillRequest], list[str]]:
    entry_orders = plan.entry_orders
    if not entry_orders or suppress_buys:
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


def _target_exposure_requests(
    *,
    plan: RebalancePlan,
    current_state: PortfolioState,
    execution_bars: DailyBars,
    blocked_sell_symbols: set[str],
    suppress_buys: bool,
) -> tuple[tuple[ExecutionFillRequest, ...], list[str]]:
    desired = plan.desired_symbols
    target_exposure = plan.target_exposure
    if target_exposure is None:
        raise OrderSizingError("target exposure plan is missing target_exposure")
    if not desired:
        requests = tuple(
            request
            for request in _exit_requests(plan, execution_bars)
            if request.symbol not in blocked_sell_symbols
        )
        return requests, []

    current_positions = current_state.positions_by_symbol
    reference_nav = _reference_nav(
        current_state=current_state,
        execution_bars=execution_bars,
    )
    target_per_symbol = (
        reference_nav * target_exposure / Decimal(len(desired))
    )

    requests: list[ExecutionFillRequest] = []
    skipped: list[str] = []
    next_sequence = 1

    for order in plan.exit_orders:
        if order.quantity is None:
            raise OrderSizingError(f"exit order for {order.symbol} has no quantity")
        if order.symbol in blocked_sell_symbols:
            continue
        requests.append(
            ExecutionFillRequest(
                trade_date=execution_bars.trade_date,
                sequence=next_sequence,
                symbol=order.symbol,
                side=FillSide.SELL,
                quantity=order.quantity,
                reference_price=execution_bars.require(order.symbol).adjusted_open,
            )
        )
        next_sequence += 1

    for symbol in desired:
        position = current_positions.get(symbol)
        if position is None or symbol in blocked_sell_symbols:
            continue
        price = execution_bars.require(symbol).adjusted_open
        current_value = price * Decimal(position.quantity)
        quantity = _whole_shares(current_value - target_per_symbol, price)
        if quantity <= 0:
            continue
        requests.append(
            ExecutionFillRequest(
                trade_date=execution_bars.trade_date,
                sequence=next_sequence,
                symbol=symbol,
                side=FillSide.SELL,
                quantity=min(quantity, position.quantity),
                reference_price=price,
            )
        )
        next_sequence += 1

    if suppress_buys:
        return tuple(requests), skipped

    cash_after_sells = current_state.cash + sum(
        (
            request.reference_price * Decimal(request.quantity)
            for request in requests
            if request.side is FillSide.SELL
        ),
        Decimal("0"),
    )
    buy_candidates: list[tuple[str, Decimal, Decimal]] = []
    for symbol in desired:
        price = execution_bars.require(symbol).adjusted_open
        position = current_positions.get(symbol)
        current_quantity = 0 if position is None else position.quantity
        current_value = price * Decimal(current_quantity)
        gap = target_per_symbol - current_value
        if gap > Decimal("0"):
            buy_candidates.append((symbol, price, gap))

    for symbol, price, gap in buy_candidates:
        remaining_buys = len(buy_candidates) - len(
            [request for request in requests if request.side is FillSide.BUY]
        )
        if remaining_buys <= 0:
            break
        per_symbol_budget = min(gap, cash_after_sells / Decimal(remaining_buys))
        quantity = _whole_shares(per_symbol_budget, price)
        if quantity <= 0:
            skipped.append(symbol)
            continue
        turnover = price * Decimal(quantity)
        cash_after_sells -= turnover
        requests.append(
            ExecutionFillRequest(
                trade_date=execution_bars.trade_date,
                sequence=next_sequence,
                symbol=symbol,
                side=FillSide.BUY,
                quantity=quantity,
                reference_price=price,
            )
        )
        next_sequence += 1

    return tuple(requests), skipped


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

    reference_nav = _reference_nav(
        current_state=current_state,
        execution_bars=execution_bars,
    )
    return reference_nav / Decimal(len(plan.desired_symbols))


def _reference_nav(
    *,
    current_state: PortfolioState,
    execution_bars: DailyBars,
) -> Decimal:
    return current_state.cash + sum(
        (
            execution_bars.require(position.symbol).adjusted_open
            * Decimal(position.quantity)
            for position in current_state.positions
        ),
        Decimal("0"),
    )


def _symbol(value: str) -> str:
    symbol = value.strip().upper() if isinstance(value, str) else ""
    if not symbol:
        raise ValueError("symbol must be non-blank")
    return symbol
