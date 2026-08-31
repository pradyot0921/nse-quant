from datetime import date
from decimal import Decimal

import pytest

from nse_quant.backtest.data import BacktestBar, DailyBars, BacktestDataError
from nse_quant.backtest.portfolio import FillSide, PortfolioState, Position
from nse_quant.backtest.rebalance import plan_rebalance_orders
from nse_quant.backtest.sizing import OrderSizingError, size_rebalance_orders


SIGNAL_DAY = date(2026, 8, 21)
EXECUTION_DAY = date(2026, 8, 24)


def bar(symbol, open_price):
    return BacktestBar(
        trade_date=EXECUTION_DAY,
        symbol=symbol,
        adjusted_open=Decimal(open_price),
        adjusted_high=Decimal(open_price),
        adjusted_low=Decimal(open_price),
        adjusted_close=Decimal(open_price),
        adjusted_volume=Decimal("1000"),
        raw_traded_value=Decimal("100000"),
    )


def daily_bars(*bars):
    return DailyBars(trade_date=EXECUTION_DAY, bars=bars)


def state(cash, *positions):
    return PortfolioState(cash=cash, positions=positions)


def position(symbol, quantity):
    return Position(symbol=symbol, quantity=quantity)


def test_sizing_converts_rebalance_plan_to_execution_requests():
    current_state = state("100", position("AAA", 10), position("KEEP", 5))
    plan = plan_rebalance_orders(
        signal_date=SIGNAL_DAY,
        current_state=current_state,
        desired_symbols=["KEEP", "BBB", "CCC"],
    )

    sized = size_rebalance_orders(
        plan=plan,
        current_state=current_state,
        execution_bars=daily_bars(
            bar("AAA", "20"),
            bar("BBB", "30"),
            bar("CCC", "40"),
            bar("KEEP", "50"),
        ),
        max_positions=3,
    )

    assert sized.execution_date == EXECUTION_DAY
    assert sized.skipped_entries == ()
    assert [
        (request.sequence, request.side, request.symbol, request.quantity, request.reference_price)
        for request in sized.requests
    ] == [
        (1, FillSide.SELL, "AAA", 10, Decimal("20")),
        (2, FillSide.BUY, "BBB", 5, Decimal("30")),
        (3, FillSide.BUY, "CCC", 3, Decimal("40")),
    ]


def test_sizing_reduces_gap_entry_so_costs_do_not_create_negative_cash():
    current_state = state("100")
    plan = plan_rebalance_orders(
        signal_date=SIGNAL_DAY,
        current_state=current_state,
        desired_symbols=["BBB"],
    )

    sized = size_rebalance_orders(
        plan=plan,
        current_state=current_state,
        execution_bars=daily_bars(bar("BBB", "100")),
        max_positions=1,
    )

    assert sized.requests == ()
    assert sized.skipped_entries == ("BBB",)


def test_sizing_resizes_last_entry_until_whole_plan_is_affordable():
    current_state = state("200")
    plan = plan_rebalance_orders(
        signal_date=SIGNAL_DAY,
        current_state=current_state,
        desired_symbols=["AAA", "BBB"],
    )

    sized = size_rebalance_orders(
        plan=plan,
        current_state=current_state,
        execution_bars=daily_bars(bar("AAA", "100"), bar("BBB", "50")),
        max_positions=2,
    )

    assert [(request.symbol, request.quantity) for request in sized.requests] == [
        ("AAA", 1),
        ("BBB", 1),
    ]


def test_sizing_caps_new_entries_at_target_position_budget():
    current_state = state("1000", position("AAA", 1), position("BBB", 1))
    plan = plan_rebalance_orders(
        signal_date=SIGNAL_DAY,
        current_state=current_state,
        desired_symbols=["AAA", "BBB", "CCC"],
    )

    sized = size_rebalance_orders(
        plan=plan,
        current_state=current_state,
        execution_bars=daily_bars(
            bar("AAA", "100"),
            bar("BBB", "100"),
            bar("CCC", "50"),
        ),
        max_positions=3,
    )

    assert [(request.symbol, request.quantity) for request in sized.requests] == [
        ("CCC", 8),
    ]


def test_sizing_rejects_desired_symbols_above_max_positions():
    current_state = state("1000")
    plan = plan_rebalance_orders(
        signal_date=SIGNAL_DAY,
        current_state=current_state,
        desired_symbols=["AAA", "BBB", "CCC"],
    )

    with pytest.raises(OrderSizingError, match="max_positions"):
        size_rebalance_orders(
            plan=plan,
            current_state=current_state,
            execution_bars=daily_bars(
                bar("AAA", "10"),
                bar("BBB", "10"),
                bar("CCC", "10"),
            ),
            max_positions=2,
        )


def test_sizing_rejects_same_day_execution():
    current_state = state("1000")
    plan = plan_rebalance_orders(
        signal_date=SIGNAL_DAY,
        current_state=current_state,
        desired_symbols=["AAA"],
    )

    with pytest.raises(OrderSizingError, match="after signal date"):
        size_rebalance_orders(
            plan=plan,
            current_state=current_state,
            execution_bars=DailyBars(trade_date=SIGNAL_DAY, bars=(bar("AAA", "10"),)),
            max_positions=1,
        )


def test_sizing_requires_execution_bar_for_every_ordered_symbol():
    current_state = state("1000")
    plan = plan_rebalance_orders(
        signal_date=SIGNAL_DAY,
        current_state=current_state,
        desired_symbols=["AAA"],
    )

    with pytest.raises(BacktestDataError, match="missing processed bar"):
        size_rebalance_orders(
            plan=plan,
            current_state=current_state,
            execution_bars=daily_bars(),
            max_positions=1,
        )
