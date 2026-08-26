"""Execution-cost adapter for explicit backtest fills."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

from nse_quant.backtest.portfolio import FillSide, PortfolioFill
from nse_quant.costs.india_equity import (
    DPChargeProfile,
    CostProfile,
    DailyCostBreakdown,
    Fill,
    TradeSide,
    ZERODHA_NSE_DELIVERY_2026_08,
    calculate_daily_costs,
)

MONEY = Decimal("0.01")
ZERO = Decimal("0")


@dataclass(frozen=True)
class ExecutionFillRequest:
    trade_date: date
    sequence: int
    symbol: str
    side: FillSide | str
    quantity: int
    reference_price: Decimal | str | int

    def __post_init__(self) -> None:
        if not isinstance(self.trade_date, date):
            raise TypeError("trade_date must be a date")
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int):
            raise TypeError("sequence must be an integer")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an integer")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")

        reference_price = _decimal(self.reference_price, "reference_price")
        if reference_price <= ZERO:
            raise ValueError("reference_price must be positive")

        object.__setattr__(self, "symbol", _symbol(self.symbol))
        object.__setattr__(self, "side", FillSide(self.side))
        object.__setattr__(self, "reference_price", reference_price)


@dataclass(frozen=True)
class ExecutionCostResult:
    portfolio_fills: tuple[PortfolioFill, ...]
    daily_costs: tuple[DailyCostBreakdown, ...]

    @property
    def total_cost(self) -> Decimal:
        return money(sum((day.total_cost for day in self.daily_costs), ZERO))


def build_portfolio_fills_with_costs(
    requests: Iterable[ExecutionFillRequest],
    *,
    slippage_rate: Decimal | str | int = Decimal("0.0005"),
    cost_profile: CostProfile = ZERODHA_NSE_DELIVERY_2026_08,
    dp_profile: DPChargeProfile | str = DPChargeProfile.MALE_PRIMARY,
) -> ExecutionCostResult:
    """Apply adverse slippage and allocated daily costs to portfolio fills."""

    rate = _slippage_rate(slippage_rate)
    ordered_requests = tuple(sorted(requests, key=_request_key))
    grouped: dict[date, list[ExecutionFillRequest]] = {}
    for request in ordered_requests:
        grouped.setdefault(request.trade_date, []).append(request)

    portfolio_fills: list[PortfolioFill] = []
    daily_costs: list[DailyCostBreakdown] = []
    for trade_date, day_requests in sorted(grouped.items()):
        cost_fills = tuple(_cost_fill(request, rate) for request in day_requests)
        day_costs = calculate_daily_costs(
            cost_fills,
            profile=cost_profile,
            dp_profile=dp_profile,
        )
        daily_costs.append(day_costs)

        for request, cost_fill, allocation in zip(
            day_requests, cost_fills, day_costs.allocations, strict=True
        ):
            portfolio_fills.append(
                PortfolioFill(
                    trade_date=trade_date,
                    sequence=request.sequence,
                    symbol=request.symbol,
                    side=request.side,
                    quantity=request.quantity,
                    price=cost_fill.price,
                    fees=allocation.total_cost,
                )
            )

    return ExecutionCostResult(
        portfolio_fills=tuple(portfolio_fills),
        daily_costs=tuple(daily_costs),
    )


def _cost_fill(request: ExecutionFillRequest, slippage_rate: Decimal) -> Fill:
    return Fill(
        trade_date=request.trade_date,
        symbol=request.symbol,
        side=_trade_side(request.side),
        quantity=request.quantity,
        price=_slipped_price(request.side, request.reference_price, slippage_rate),
    )


def _slipped_price(
    side: FillSide, reference_price: Decimal, slippage_rate: Decimal
) -> Decimal:
    multiplier = Decimal("1") + slippage_rate
    if side is FillSide.SELL:
        multiplier = Decimal("1") - slippage_rate
    return money(reference_price * multiplier)


def _trade_side(side: FillSide) -> TradeSide:
    if side is FillSide.BUY:
        return TradeSide.BUY
    return TradeSide.SELL


def _request_key(request: ExecutionFillRequest) -> tuple[date, int, str, str]:
    return (request.trade_date, request.sequence, request.symbol, request.side.value)


def _slippage_rate(value: Decimal | str | int) -> Decimal:
    rate = _decimal(value, "slippage_rate")
    if rate < ZERO:
        raise ValueError("slippage_rate must be non-negative")
    if rate >= Decimal("1"):
        raise ValueError("slippage_rate must be less than 1")
    return rate


def money(amount: Decimal) -> Decimal:
    return amount.quantize(MONEY, rounding=ROUND_HALF_UP)


def _decimal(value: Decimal | str | int, field_name: str) -> Decimal:
    if isinstance(value, float):
        raise TypeError(f"{field_name} must not be a binary float")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        return Decimal(value)
    raise TypeError(f"{field_name} must be Decimal, str, or int")


def _symbol(value: str) -> str:
    symbol = value.strip().upper() if isinstance(value, str) else ""
    if not symbol:
        raise ValueError("symbol must be non-blank")
    return symbol
