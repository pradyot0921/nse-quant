"""Symbol-level rebalance order planning."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Iterable

from nse_quant.backtest.portfolio import FillSide, PortfolioState


class RebalancePlanError(RuntimeError):
    """Raised when rebalance planning inputs are invalid."""


class RebalanceReason(StrEnum):
    EXIT_NOT_DESIRED = "EXIT_NOT_DESIRED"
    ENTER_DESIRED = "ENTER_DESIRED"


@dataclass(frozen=True)
class PlannedRebalanceOrder:
    signal_date: date
    sequence: int
    symbol: str
    side: FillSide
    quantity: int | None
    reason: RebalanceReason


@dataclass(frozen=True)
class RebalancePlan:
    signal_date: date
    desired_symbols: tuple[str, ...]
    orders: tuple[PlannedRebalanceOrder, ...]

    @property
    def exit_orders(self) -> tuple[PlannedRebalanceOrder, ...]:
        return tuple(order for order in self.orders if order.side is FillSide.SELL)

    @property
    def entry_orders(self) -> tuple[PlannedRebalanceOrder, ...]:
        return tuple(order for order in self.orders if order.side is FillSide.BUY)


def plan_rebalance_orders(
    *,
    signal_date: date,
    current_state: PortfolioState,
    desired_symbols: Iterable[str],
) -> RebalancePlan:
    """Plan exits before entries from current holdings and desired symbols."""

    if not isinstance(signal_date, date):
        raise TypeError("signal_date must be a date")

    desired = _desired_symbols(desired_symbols)
    desired_set = set(desired)
    positions = current_state.positions_by_symbol

    orders: list[PlannedRebalanceOrder] = []
    sequence = 1

    for symbol in sorted(set(positions) - desired_set):
        orders.append(
            PlannedRebalanceOrder(
                signal_date=signal_date,
                sequence=sequence,
                symbol=symbol,
                side=FillSide.SELL,
                quantity=positions[symbol].quantity,
                reason=RebalanceReason.EXIT_NOT_DESIRED,
            )
        )
        sequence += 1

    for symbol in desired:
        if symbol in positions:
            continue
        orders.append(
            PlannedRebalanceOrder(
                signal_date=signal_date,
                sequence=sequence,
                symbol=symbol,
                side=FillSide.BUY,
                quantity=None,
                reason=RebalanceReason.ENTER_DESIRED,
            )
        )
        sequence += 1

    return RebalancePlan(
        signal_date=signal_date,
        desired_symbols=desired,
        orders=tuple(orders),
    )


def _desired_symbols(values: Iterable[str]) -> tuple[str, ...]:
    symbols = tuple(_symbol(value) for value in values)
    duplicates = sorted({symbol for symbol in symbols if symbols.count(symbol) > 1})
    if duplicates:
        raise RebalancePlanError(f"duplicate desired symbols: {duplicates}")
    return symbols


def _symbol(value: str) -> str:
    symbol = value.strip().upper() if isinstance(value, str) else ""
    if not symbol:
        raise ValueError("symbol must be non-blank")
    return symbol
