from datetime import date
from decimal import Decimal

import pytest

from nse_quant.backtest.data import BacktestBar, DailyBars
from nse_quant.backtest.engine import run_day_loop
from nse_quant.backtest.execution import (
    ExecutionFillRequest,
    build_portfolio_fills_with_costs,
)
from nse_quant.backtest.portfolio import FillSide, PortfolioState
from nse_quant.costs.india_equity import Fill, TradeSide, calculate_daily_costs


def request(trade_date, symbol, side, quantity, price, sequence=0):
    return ExecutionFillRequest(
        trade_date=trade_date,
        sequence=sequence,
        symbol=symbol,
        side=side,
        quantity=quantity,
        reference_price=price,
    )


def bar(trade_date, symbol, close):
    return BacktestBar(
        trade_date=trade_date,
        symbol=symbol,
        adjusted_open=Decimal(close),
        adjusted_high=Decimal(close),
        adjusted_low=Decimal(close),
        adjusted_close=Decimal(close),
        adjusted_volume=Decimal("1000"),
        raw_traded_value=Decimal("100000"),
    )


def test_execution_applies_adverse_slippage_and_daily_cost_allocations():
    trade_date = date(2026, 8, 19)

    result = build_portfolio_fills_with_costs(
        [
            request(trade_date, "abc", FillSide.BUY, 10, "100.00", sequence=2),
            request(trade_date, "abc", FillSide.SELL, 5, "100.00", sequence=1),
        ],
        slippage_rate="0.0005",
    )

    assert [fill.sequence for fill in result.portfolio_fills] == [1, 2]
    assert [fill.price for fill in result.portfolio_fills] == [
        Decimal("99.95"),
        Decimal("100.05"),
    ]

    expected_costs = calculate_daily_costs(
        [
            Fill(trade_date, "ABC", TradeSide.SELL, 5, Decimal("99.95")),
            Fill(trade_date, "ABC", TradeSide.BUY, 10, Decimal("100.05")),
        ]
    )
    assert result.daily_costs[0].total_cost == expected_costs.total_cost
    assert sum((fill.fees for fill in result.portfolio_fills), Decimal("0")) == (
        expected_costs.total_cost
    )


def test_execution_groups_costs_by_trade_date():
    result = build_portfolio_fills_with_costs(
        [
            request(date(2026, 8, 20), "XYZ", FillSide.BUY, 2, "50"),
            request(date(2026, 8, 19), "ABC", FillSide.BUY, 1, "100"),
        ]
    )

    assert [cost.trade_date for cost in result.daily_costs] == [
        date(2026, 8, 19),
        date(2026, 8, 20),
    ]
    assert [fill.symbol for fill in result.portfolio_fills] == ["ABC", "XYZ"]


def test_execution_fills_can_run_through_day_loop():
    trade_date = date(2026, 8, 19)
    execution = build_portfolio_fills_with_costs(
        [request(trade_date, "ABC", FillSide.BUY, 5, "100")],
        slippage_rate="0.0005",
    )

    result = run_day_loop(
        [DailyBars(trade_date, (bar(trade_date, "ABC", "101"),))],
        starting_state=PortfolioState.starting_cash("1000"),
        fills=execution.portfolio_fills,
    )

    fill = execution.portfolio_fills[0]
    expected_cash = Decimal("1000.00") - fill.turnover - fill.fees
    assert result.ending_state.cash == expected_cash
    assert result.final_snapshot.nav == expected_cash + Decimal("505.00")


def test_execution_rejects_invalid_slippage_rates():
    with pytest.raises(ValueError, match="non-negative"):
        build_portfolio_fills_with_costs([], slippage_rate="-0.01")

    with pytest.raises(ValueError, match="less than 1"):
        build_portfolio_fills_with_costs([], slippage_rate="1")

    with pytest.raises(TypeError, match="binary float"):
        build_portfolio_fills_with_costs([], slippage_rate=0.0005)


def test_execution_request_rejects_binary_float_reference_price():
    with pytest.raises(TypeError, match="binary float"):
        request(date(2026, 8, 19), "ABC", FillSide.BUY, 1, 100.0)
