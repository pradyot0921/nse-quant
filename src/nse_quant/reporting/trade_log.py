"""Trade-log rows for executed fills and allocated costs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from nse_quant.backtest.execution import ExecutionCostResult
from nse_quant.backtest.portfolio import FillSide, PortfolioFill
from nse_quant.costs.india_equity import AllocatedFillCost, TradeSide


class TradeLogError(RuntimeError):
    """Raised when execution results cannot be rendered as a trade log."""


@dataclass(frozen=True)
class TradeLogRow:
    trade_date: date
    sequence: int
    symbol: str
    side: FillSide
    quantity: int
    price: Decimal
    turnover: Decimal
    brokerage: Decimal
    stt_buy: Decimal
    stt_sell: Decimal
    exchange_transaction_charge: Decimal
    sebi_turnover_charge: Decimal
    gst: Decimal
    stamp_duty: Decimal
    dp_charges: Decimal
    total_cost: Decimal
    allocation_note: str


def trade_log_rows_from_execution(
    execution: ExecutionCostResult,
) -> tuple[TradeLogRow, ...]:
    """Render allocated fill costs as reporting rows."""

    allocations = tuple(
        allocation
        for daily_costs in execution.daily_costs
        for allocation in daily_costs.allocations
    )
    fills = execution.portfolio_fills
    if len(fills) != len(allocations):
        raise TradeLogError("portfolio fills and cost allocations differ")

    rows = []
    for fill, allocation in zip(fills, allocations, strict=True):
        _validate_alignment(fill, allocation)
        rows.append(
            TradeLogRow(
                trade_date=fill.trade_date,
                sequence=fill.sequence,
                symbol=fill.symbol,
                side=fill.side,
                quantity=fill.quantity,
                price=fill.price,
                turnover=fill.turnover,
                brokerage=allocation.brokerage,
                stt_buy=allocation.stt_buy,
                stt_sell=allocation.stt_sell,
                exchange_transaction_charge=allocation.exchange_transaction_charge,
                sebi_turnover_charge=allocation.sebi_turnover_charge,
                gst=allocation.gst,
                stamp_duty=allocation.stamp_duty,
                dp_charges=allocation.dp_charges,
                total_cost=allocation.total_cost,
                allocation_note=allocation.allocation_note,
            )
        )

    return tuple(sorted(rows, key=_row_key))


def _validate_alignment(
    fill: PortfolioFill, allocation: AllocatedFillCost
) -> None:
    allocated_fill = allocation.fill
    if (
        fill.trade_date != allocated_fill.trade_date
        or fill.symbol != allocated_fill.symbol
        or _trade_side(fill.side) is not allocated_fill.side
        or fill.quantity != allocated_fill.quantity
        or fill.price != allocated_fill.price
        or fill.fees != allocation.total_cost
    ):
        raise TradeLogError("portfolio fill and cost allocation do not align")


def _trade_side(side: FillSide) -> TradeSide:
    if side is FillSide.BUY:
        return TradeSide.BUY
    return TradeSide.SELL


def _row_key(row: TradeLogRow) -> tuple[date, int, str, str]:
    return (row.trade_date, row.sequence, row.symbol, row.side.value)
