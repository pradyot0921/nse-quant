from datetime import date
from decimal import Decimal

import pytest

from nse_quant.backtest.execution import (
    ExecutionCostResult,
    ExecutionFillRequest,
    build_portfolio_fills_with_costs,
)
from nse_quant.backtest.portfolio import FillSide
from nse_quant.reporting.trade_log import (
    TradeLogError,
    trade_log_rows_from_execution,
)


def request(trade_date, sequence, symbol, side, quantity, price):
    return ExecutionFillRequest(
        trade_date=trade_date,
        sequence=sequence,
        symbol=symbol,
        side=side,
        quantity=quantity,
        reference_price=price,
    )


def test_trade_log_rows_itemise_allocated_cost_components():
    trade_date = date(2026, 8, 19)
    execution = build_portfolio_fills_with_costs(
        [
            request(trade_date, 2, "ABC", FillSide.BUY, 10, "100"),
            request(trade_date, 1, "ABC", FillSide.SELL, 5, "100"),
        ],
        slippage_rate="0",
    )

    rows = trade_log_rows_from_execution(execution)

    assert [(row.sequence, row.side, row.symbol) for row in rows] == [
        (1, FillSide.SELL, "ABC"),
        (2, FillSide.BUY, "ABC"),
    ]
    assert rows[0].turnover == Decimal("500.00")
    assert rows[1].turnover == Decimal("1000.00")
    assert rows[0].dp_charges > Decimal("0")
    assert rows[1].stamp_duty > Decimal("0")
    assert rows[0].allocation_note == (
        "REPORTING ALLOCATION; DAILY TOTAL IS AUTHORITATIVE"
    )


def test_trade_log_cost_components_sum_back_to_execution_costs():
    trade_date = date(2026, 8, 19)
    execution = build_portfolio_fills_with_costs(
        [
            request(trade_date, 1, "AAA", FillSide.BUY, 7, "111.10"),
            request(trade_date, 2, "BBB", FillSide.SELL, 3, "222.20"),
            request(trade_date, 3, "CCC", FillSide.SELL, 2, "333.30"),
        ],
        slippage_rate="0",
    )

    rows = trade_log_rows_from_execution(execution)
    daily_costs = execution.daily_costs[0]

    assert sum((row.total_cost for row in rows), Decimal("0")) == daily_costs.total_cost
    assert sum((row.brokerage for row in rows), Decimal("0")) == daily_costs.brokerage
    assert sum((row.stt_buy for row in rows), Decimal("0")) == daily_costs.stt_buy
    assert sum((row.stt_sell for row in rows), Decimal("0")) == daily_costs.stt_sell
    assert sum((row.exchange_transaction_charge for row in rows), Decimal("0")) == (
        daily_costs.exchange_transaction_charge
    )
    assert sum((row.sebi_turnover_charge for row in rows), Decimal("0")) == (
        daily_costs.sebi_turnover_charge
    )
    assert sum((row.gst for row in rows), Decimal("0")) == daily_costs.gst
    assert sum((row.stamp_duty for row in rows), Decimal("0")) == daily_costs.stamp_duty
    assert sum((row.dp_charges for row in rows), Decimal("0")) == daily_costs.dp_charges


def test_trade_log_rows_preserve_multiple_trade_dates():
    execution = build_portfolio_fills_with_costs(
        [
            request(date(2026, 8, 20), 1, "BBB", FillSide.BUY, 1, "50"),
            request(date(2026, 8, 19), 1, "AAA", FillSide.BUY, 1, "100"),
        ],
        slippage_rate="0",
    )

    rows = trade_log_rows_from_execution(execution)

    assert [(row.trade_date, row.symbol) for row in rows] == [
        (date(2026, 8, 19), "AAA"),
        (date(2026, 8, 20), "BBB"),
    ]


def test_trade_log_empty_execution_has_no_rows():
    execution = build_portfolio_fills_with_costs([])

    assert trade_log_rows_from_execution(execution) == ()


def test_trade_log_rejects_mismatched_fills_and_allocations():
    execution = build_portfolio_fills_with_costs(
        [request(date(2026, 8, 19), 1, "AAA", FillSide.BUY, 1, "100")],
        slippage_rate="0",
    )
    mismatched = ExecutionCostResult(
        portfolio_fills=execution.portfolio_fills,
        daily_costs=(),
    )

    with pytest.raises(TradeLogError, match="differ"):
        trade_log_rows_from_execution(mismatched)
