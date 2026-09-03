from datetime import date, timedelta
from decimal import Decimal

import pytest

from nse_quant.backtest.data import BacktestBar, DailyBars
from nse_quant.data.benchmark import NIFTY100_TRI_NAME, TriBenchmarkBar
from nse_quant.strategies.momentum import (
    MarketRegime,
    MomentumSignalError,
    generate_weekly_hysteresis_momentum_signals,
    generate_weekly_momentum_signals,
    generate_weekly_regime_filtered_hysteresis_momentum_signals,
    summarize_regime_exposure,
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


def benchmark(trade_date, value):
    return TriBenchmarkBar(
        index_name=NIFTY100_TRI_NAME,
        trade_date=trade_date,
        total_return_index=Decimal(value),
        net_total_return_index=None,
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


def test_b004_regime_is_unavailable_until_200_benchmark_observations():
    dates = sessions(date(2026, 1, 1), 199)
    daily = [day(trade_date, {"AAA": "100"}) for trade_date in dates]

    signals = generate_weekly_regime_filtered_hysteresis_momentum_signals(
        daily,
        benchmark_bars=[benchmark(trade_date, "100") for trade_date in dates],
        universe=["AAA"],
        lookback_sessions=1,
    )

    assert signals[-1].regime is MarketRegime.NOT_AVAILABLE
    assert signals[-1].sma200 is None
    assert signals[-1].desired_symbols == ()


def test_b004_regime_sma200_is_available_on_exactly_200th_observation():
    dates = sessions(date(2026, 1, 1), 200)
    daily = [day(trade_date, {"AAA": "100"}) for trade_date in dates]

    signals = generate_weekly_regime_filtered_hysteresis_momentum_signals(
        daily,
        benchmark_bars=[benchmark(trade_date, "100") for trade_date in dates],
        universe=["AAA"],
        lookback_sessions=1,
    )

    assert signals[-1].regime is MarketRegime.RISK_OFF
    assert signals[-1].benchmark_tri == Decimal("100")
    assert signals[-1].sma200 == Decimal("100")
    assert signals[-1].desired_symbols == ()


@pytest.mark.parametrize(
    ("last_tri", "expected"),
    [
        ("101", MarketRegime.RISK_ON),
        ("100", MarketRegime.RISK_OFF),
        ("99", MarketRegime.RISK_OFF),
    ],
)
def test_b004_regime_threshold_uses_strict_tri_greater_than_sma(last_tri, expected):
    dates = sessions(date(2026, 1, 1), 200)
    daily = [day(trade_date, {"AAA": str(100 + index)}) for index, trade_date in enumerate(dates)]
    benchmark_bars = [benchmark(trade_date, "100") for trade_date in dates[:-1]]
    benchmark_bars.append(benchmark(dates[-1], last_tri))

    signals = generate_weekly_regime_filtered_hysteresis_momentum_signals(
        daily,
        benchmark_bars=benchmark_bars,
        universe=["AAA"],
        lookback_sessions=1,
    )

    assert signals[-1].regime is expected


def test_b004_risk_on_delegates_to_b003_hysteresis_ranking():
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
    benchmark_bars = [
        benchmark(dates[0], "100"),
        benchmark(dates[1], "102"),
        benchmark(dates[2], "104"),
        benchmark(dates[3], "106"),
        benchmark(dates[4], "108"),
    ]

    signals = generate_weekly_regime_filtered_hysteresis_momentum_signals(
        daily,
        benchmark_bars=benchmark_bars,
        universe=["AAA", "BBB", "CCC"],
        lookback_sessions=1,
        max_positions=1,
        entry_rank=1,
        hold_rank=2,
        regime_sma_sessions=2,
    )

    assert [signal.regime for signal in signals] == [
        MarketRegime.RISK_ON,
        MarketRegime.RISK_ON,
        MarketRegime.RISK_ON,
    ]
    assert [signal.desired_symbols for signal in signals] == [
        ("AAA",),
        ("AAA",),
        ("CCC",),
    ]


def test_b004_regime_summary_counts_available_sessions_and_weekly_state_changes():
    dates = sessions(date(2026, 1, 1), 6)
    daily = [day(trade_date, {"AAA": str(100 + index)}) for index, trade_date in enumerate(dates)]
    benchmark_bars = [
        benchmark(dates[0], "100"),
        benchmark(dates[1], "102"),
        benchmark(dates[2], "101"),
        benchmark(dates[3], "100"),
        benchmark(dates[4], "103"),
        benchmark(dates[5], "99"),
    ]
    weekly_signals = generate_weekly_regime_filtered_hysteresis_momentum_signals(
        daily,
        benchmark_bars=benchmark_bars,
        universe=["AAA"],
        lookback_sessions=1,
        regime_sma_sessions=2,
    )

    summary = summarize_regime_exposure(
        daily,
        benchmark_bars=benchmark_bars,
        weekly_signals=weekly_signals,
        regime_sma_sessions=2,
    )

    assert summary.unavailable_sessions == 1
    assert summary.risk_on_sessions == 2
    assert summary.risk_off_sessions == 3
    assert summary.weekly_state_changes == 1
    assert summary.risk_on_share == Decimal("0.4")
    assert summary.risk_off_share == Decimal("0.6")


def test_b004_regime_rejects_missing_required_benchmark_observation():
    dates = sessions(date(2026, 1, 1), 5)
    daily = [day(trade_date, {"AAA": "100"}) for trade_date in dates]

    with pytest.raises(MomentumSignalError, match="missing benchmark observations"):
        generate_weekly_regime_filtered_hysteresis_momentum_signals(
            daily,
            benchmark_bars=[benchmark(trade_date, "100") for trade_date in dates[:-1]],
            universe=["AAA"],
            lookback_sessions=1,
            regime_sma_sessions=2,
        )
