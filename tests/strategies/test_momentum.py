from datetime import date, timedelta
from decimal import Decimal

import pytest

from nse_quant.backtest.data import BacktestBar, DailyBars
from nse_quant.strategies.momentum import (
    MomentumSignalError,
    generate_weekly_hysteresis_momentum_signals,
    generate_weekly_momentum_signals,
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


def day(trade_date, prices):
    return DailyBars(
        trade_date=trade_date,
        bars=tuple(bar(trade_date, symbol, close) for symbol, close in prices.items()),
    )


def sessions(start, count):
    current = start
    dates = []
    while len(dates) < count:
        if current.weekday() < 5:
            dates.append(current)
        current += timedelta(days=1)
    return dates


def test_weekly_momentum_ranks_symbols_on_last_session_of_each_week():
    dates = sessions(date(2026, 1, 5), 12)
    daily = [
        day(
            trade_date,
            {
                "AAA": str(100 + index),
                "BBB": str(100 + index * 2),
                "CCC": str(100 + index * 3),
            },
        )
        for index, trade_date in enumerate(dates)
    ]

    signals = generate_weekly_momentum_signals(
        daily,
        universe=["AAA", "BBB", "CCC"],
        lookback_sessions=5,
        max_positions=2,
    )

    assert [signal.signal_date for signal in signals] == [
        date(2026, 1, 16),
        date(2026, 1, 20),
    ]
    assert signals[0].desired_symbols == ("CCC", "BBB")
    assert [score.rank for score in signals[0].scores] == [1, 2, 3]


def test_momentum_uses_adjusted_close_from_exact_lookback_session():
    dates = sessions(date(2026, 1, 5), 6)
    daily = [
        day(dates[0], {"AAA": "100", "BBB": "100"}),
        day(dates[1], {"AAA": "1", "BBB": "1"}),
        day(dates[2], {"AAA": "1", "BBB": "1"}),
        day(dates[3], {"AAA": "1", "BBB": "1"}),
        day(dates[4], {"AAA": "1", "BBB": "1"}),
        day(dates[5], {"AAA": "130", "BBB": "120"}),
    ]

    signals = generate_weekly_momentum_signals(
        daily,
        universe=["AAA", "BBB"],
        lookback_sessions=5,
        max_positions=2,
    )

    assert signals[0].signal_date == dates[5]
    assert signals[0].scores[0].symbol == "AAA"
    assert signals[0].scores[0].momentum == Decimal("0.3")
    assert signals[0].scores[1].momentum == Decimal("0.2")


def test_missing_current_or_lookback_bar_makes_symbol_ineligible():
    dates = sessions(date(2026, 1, 5), 6)
    daily = [
        day(dates[0], {"AAA": "100", "BBB": "100", "CCC": "100"}),
        day(dates[1], {"AAA": "100", "BBB": "100", "CCC": "100"}),
        day(dates[2], {"AAA": "100", "BBB": "100", "CCC": "100"}),
        day(dates[3], {"AAA": "100", "BBB": "100", "CCC": "100"}),
        day(dates[4], {"AAA": "100", "BBB": "100", "CCC": "100"}),
        day(dates[5], {"AAA": "120", "BBB": "110"}),
    ]

    signals = generate_weekly_momentum_signals(
        daily,
        universe=["AAA", "BBB", "CCC", "MISSING"],
        lookback_sessions=5,
        max_positions=3,
    )

    assert signals[0].desired_symbols == ("AAA", "BBB")
    assert [score.symbol for score in signals[0].scores] == ["AAA", "BBB"]


def test_momentum_ties_break_by_symbol():
    dates = sessions(date(2026, 1, 5), 6)
    daily = [
        day(dates[0], {"BBB": "100", "AAA": "100"}),
        day(dates[1], {"BBB": "100", "AAA": "100"}),
        day(dates[2], {"BBB": "100", "AAA": "100"}),
        day(dates[3], {"BBB": "100", "AAA": "100"}),
        day(dates[4], {"BBB": "100", "AAA": "100"}),
        day(dates[5], {"BBB": "110", "AAA": "110"}),
    ]

    signals = generate_weekly_momentum_signals(
        daily,
        universe=["BBB", "AAA"],
        lookback_sessions=5,
        max_positions=2,
    )

    assert signals[0].desired_symbols == ("AAA", "BBB")


def test_weekly_hysteresis_holds_until_hold_rank_breaks():
    dates = [
        date(2026, 1, 1),
        date(2026, 1, 2),
        date(2026, 1, 5),
        date(2026, 1, 9),
        date(2026, 1, 12),
    ]
    daily = [
        day(dates[0], {"AAA": "100", "BBB": "100", "CCC": "100"}),
        day(dates[1], {"AAA": "110", "BBB": "100", "CCC": "100"}),
        day(dates[2], {"AAA": "112", "BBB": "100", "CCC": "100"}),
        day(dates[3], {"AAA": "100", "BBB": "120", "CCC": "80"}),
        day(dates[4], {"AAA": "90", "BBB": "130", "CCC": "100"}),
    ]

    signals = generate_weekly_hysteresis_momentum_signals(
        daily,
        universe=["AAA", "BBB", "CCC"],
        lookback_sessions=1,
        max_positions=1,
        entry_rank=1,
        hold_rank=2,
    )

    assert [signal.signal_date for signal in signals] == [
        dates[1],
        dates[3],
        dates[4],
    ]
    assert [signal.desired_symbols for signal in signals] == [
        ("AAA",),
        ("AAA",),
        ("CCC",),
    ]


def test_momentum_rejects_invalid_inputs():
    with pytest.raises(MomentumSignalError, match="universe is empty"):
        generate_weekly_momentum_signals([], universe=[])

    with pytest.raises(ValueError, match="lookback_sessions"):
        generate_weekly_momentum_signals([], universe=["AAA"], lookback_sessions=0)

    with pytest.raises(ValueError, match="max_positions"):
        generate_weekly_momentum_signals([], universe=["AAA"], max_positions=0)

    with pytest.raises(TypeError, match="lookback_sessions"):
        generate_weekly_momentum_signals([], universe=["AAA"], lookback_sessions=5.0)

    with pytest.raises(ValueError, match="entry_rank"):
        generate_weekly_hysteresis_momentum_signals(
            [],
            universe=["AAA"],
            entry_rank=7,
            hold_rank=6,
        )


def test_momentum_rejects_duplicate_daily_dates():
    duplicate_date = date(2026, 1, 5)

    with pytest.raises(MomentumSignalError, match="duplicate signal days"):
        generate_weekly_momentum_signals(
            [
                day(duplicate_date, {"AAA": "100"}),
                day(duplicate_date, {"AAA": "101"}),
            ],
            universe=["AAA"],
        )
