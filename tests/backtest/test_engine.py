from datetime import date
from decimal import Decimal

import pytest

from nse_quant.backtest.data import BacktestBar, DailyBars
from nse_quant.backtest.engine import BacktestEngineError, run_day_loop
from nse_quant.backtest.portfolio import (
    BacktestAccountingError,
    FillSide,
    PortfolioFill,
    PortfolioState,
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


def day(trade_date, *bars):
    return DailyBars(trade_date=trade_date, bars=bars)


def fill(trade_date, symbol, side, quantity, price, sequence=0, fees="0"):
    return PortfolioFill(
        trade_date=trade_date,
        sequence=sequence,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        fees=fees,
    )


def test_day_loop_applies_scheduled_fills_and_marks_nav_each_day():
    result = run_day_loop(
        [
            day(date(2026, 8, 20), bar(date(2026, 8, 20), "ABC", "105")),
            day(date(2026, 8, 19), bar(date(2026, 8, 19), "ABC", "100")),
            day(date(2026, 8, 21), bar(date(2026, 8, 21), "ABC", "110")),
        ],
        starting_state=PortfolioState.starting_cash("1000"),
        fills=[
            fill(date(2026, 8, 19), "ABC", FillSide.BUY, 5, "100", fees="1.00"),
            fill(date(2026, 8, 21), "ABC", FillSide.SELL, 2, "110", fees="0.50"),
        ],
    )

    assert [snapshot.trade_date for snapshot in result.snapshots] == [
        date(2026, 8, 19),
        date(2026, 8, 20),
        date(2026, 8, 21),
    ]
    assert [snapshot.nav for snapshot in result.snapshots] == [
        Decimal("999.00"),
        Decimal("1024.00"),
        Decimal("1048.50"),
    ]
    assert result.ending_state.cash == Decimal("718.50")
    assert result.ending_state.positions_by_symbol["ABC"].quantity == 3
    assert result.final_snapshot.nav == Decimal("1048.50")


def test_day_loop_rejects_fills_on_dates_without_daily_bars():
    with pytest.raises(BacktestEngineError, match="non-session"):
        run_day_loop(
            [day(date(2026, 8, 19), bar(date(2026, 8, 19), "ABC", "100"))],
            starting_state=PortfolioState.starting_cash("1000"),
            fills=[fill(date(2026, 8, 20), "ABC", FillSide.BUY, 1, "100")],
        )


def test_day_loop_rejects_duplicate_daily_bar_dates():
    with pytest.raises(BacktestEngineError, match="duplicate backtest days"):
        run_day_loop(
            [
                day(date(2026, 8, 19), bar(date(2026, 8, 19), "ABC", "100")),
                day(date(2026, 8, 19), bar(date(2026, 8, 19), "XYZ", "100")),
            ],
            starting_state=PortfolioState.starting_cash("1000"),
        )


def test_day_loop_halts_when_held_symbol_has_no_close():
    with pytest.raises(BacktestAccountingError, match="missing close"):
        run_day_loop(
            [
                day(date(2026, 8, 19), bar(date(2026, 8, 19), "ABC", "100")),
                day(date(2026, 8, 20), bar(date(2026, 8, 20), "XYZ", "100")),
            ],
            starting_state=PortfolioState.starting_cash("1000"),
            fills=[fill(date(2026, 8, 19), "ABC", FillSide.BUY, 1, "100")],
        )
