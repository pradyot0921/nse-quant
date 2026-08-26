from datetime import date
from decimal import Decimal

import pytest

from nse_quant.backtest.data import BacktestBar, DailyBars
from nse_quant.backtest.portfolio import (
    BacktestAccountingError,
    FillSide,
    PortfolioFill,
    PortfolioState,
)


def bar(symbol, close):
    return BacktestBar(
        trade_date=date(2026, 8, 19),
        symbol=symbol,
        adjusted_open=Decimal("100"),
        adjusted_high=Decimal("120"),
        adjusted_low=Decimal("90"),
        adjusted_close=Decimal(close),
        adjusted_volume=Decimal("1000"),
        raw_traded_value=Decimal("100000"),
    )


def fill(symbol, side, quantity, price, sequence=0, fees="0"):
    return PortfolioFill(
        trade_date=date(2026, 8, 19),
        sequence=sequence,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        fees=fees,
    )


def test_portfolio_applies_buy_sell_fills_and_marks_nav_exactly():
    state = PortfolioState.starting_cash("1000.00")
    state = state.apply_fills(
        [
            fill("ABC", FillSide.BUY, 3, "100.00", sequence=1, fees="1.23"),
            fill("ABC", FillSide.SELL, 1, "110.00", sequence=2, fees="0.57"),
        ]
    )

    assert state.cash == Decimal("808.20")
    assert state.positions_by_symbol["ABC"].quantity == 2

    snapshot = state.mark_to_market(
        date(2026, 8, 19),
        DailyBars(date(2026, 8, 19), (bar("ABC", "111.00"),)),
    )

    assert snapshot.holdings_value == Decimal("222.00")
    assert snapshot.nav == Decimal("1030.20")
    assert snapshot.nav == snapshot.cash + snapshot.holdings_value


def test_portfolio_rejects_binary_float_fill_boundary():
    with pytest.raises(TypeError, match="price must not be a binary float"):
        fill("ABC", FillSide.BUY, 1, 100.0)

    with pytest.raises(TypeError, match="fees must not be a binary float"):
        fill("ABC", FillSide.BUY, 1, "100", fees=0.1)


def test_portfolio_rejects_negative_cash_and_short_sells():
    state = PortfolioState.starting_cash("100.00")

    with pytest.raises(BacktestAccountingError, match="cash negative"):
        state.apply_fills([fill("ABC", FillSide.BUY, 2, "60.00")])

    with pytest.raises(BacktestAccountingError, match="exceeds held quantity"):
        state.apply_fills([fill("ABC", FillSide.SELL, 1, "60.00")])


def test_portfolio_fill_order_is_deterministic_from_sequence():
    fills = [
        fill("XYZ", FillSide.BUY, 1, "200.00", sequence=2),
        fill("ABC", FillSide.BUY, 2, "100.00", sequence=1),
    ]

    ordered = PortfolioState.starting_cash("1000").apply_fills(fills)
    shuffled = PortfolioState.starting_cash("1000").apply_fills(tuple(reversed(fills)))

    assert ordered == shuffled
    assert [position.symbol for position in ordered.positions] == ["ABC", "XYZ"]
    assert ordered.cash == Decimal("600.00")


def test_mark_to_market_halts_when_held_symbol_has_no_close():
    state = PortfolioState.starting_cash("1000").apply_fills(
        [fill("ABC", FillSide.BUY, 1, "100.00")]
    )

    with pytest.raises(BacktestAccountingError, match="missing close"):
        state.mark_to_market(
            date(2026, 8, 19),
            DailyBars(date(2026, 8, 19), (bar("XYZ", "100.00"),)),
        )
