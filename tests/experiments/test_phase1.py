from datetime import date
from decimal import Decimal

import pytest

from nse_quant.backtest.data import BacktestBar, DailyBars
from nse_quant.backtest.portfolio import FillSide
from nse_quant.data.benchmark import NIFTY100_TRI_NAME, TriBenchmarkBar
from nse_quant.experiments.phase1 import (
    Phase1ExperimentError,
    run_weekly_hysteresis_momentum_experiment,
    run_weekly_momentum_experiment,
    run_weekly_regime_filtered_hysteresis_momentum_experiment,
)


def bar(trade_date, symbol, open_price, close_price):
    open_decimal = Decimal(open_price)
    close_decimal = Decimal(close_price)
    return BacktestBar(
        trade_date=trade_date,
        symbol=symbol,
        adjusted_open=open_decimal,
        adjusted_high=max(open_decimal, close_decimal),
        adjusted_low=min(open_decimal, close_decimal),
        adjusted_close=close_decimal,
        adjusted_volume=Decimal("1000"),
        raw_traded_value=Decimal("100000"),
    )


def day(trade_date, prices):
    return DailyBars(
        trade_date=trade_date,
        bars=tuple(
            bar(trade_date, symbol, open_price, close_price)
            for symbol, (open_price, close_price) in prices.items()
        ),
    )


def benchmark(trade_date, value):
    return TriBenchmarkBar(
        index_name=NIFTY100_TRI_NAME,
        trade_date=trade_date,
        total_return_index=Decimal(value),
        net_total_return_index=None,
    )


def test_weekly_momentum_experiment_wires_signals_backtest_turnover_and_performance():
    dates = [
        date(2026, 1, 1),
        date(2026, 1, 2),
        date(2026, 1, 5),
        date(2026, 1, 9),
        date(2026, 1, 12),
    ]
    daily_bars = [
        day(dates[0], {"AAA": ("100", "100"), "BBB": ("100", "100")}),
        day(dates[1], {"AAA": ("110", "110"), "BBB": ("100", "100")}),
        day(dates[2], {"AAA": ("112", "112"), "BBB": ("100", "100")}),
        day(dates[3], {"AAA": ("100", "100"), "BBB": ("120", "120")}),
        day(dates[4], {"AAA": ("100", "100"), "BBB": ("120", "120")}),
    ]

    result = run_weekly_momentum_experiment(
        experiment_id="B001",
        daily_bars=daily_bars,
        benchmark_bars=[
            benchmark(dates[0], "1000"),
            benchmark(dates[1], "1005"),
            benchmark(dates[2], "1010"),
            benchmark(dates[3], "1015"),
            benchmark(dates[4], "1020"),
        ],
        universe=["AAA", "BBB"],
        starting_cash="10000",
        lookback_sessions=1,
        max_positions=1,
        slippage_rate="0",
        complete_years=[2026],
    )

    assert result.experiment_id == "B001"
    assert [signal.signal_date for signal in result.signals] == [
        dates[1],
        dates[3],
        dates[4],
    ]
    assert result.signals[0].desired_symbols == ("AAA",)
    assert result.signals[1].desired_symbols == ("BBB",)
    assert [execution.execution_date for execution in result.backtest.executions] == [
        dates[2],
        dates[4],
    ]
    assert [(fill.side, fill.symbol) for fill in result.fills] == [
        (FillSide.BUY, "AAA"),
        (FillSide.SELL, "AAA"),
        (FillSide.BUY, "BBB"),
    ]
    assert len(result.execution_costs) == 2
    assert result.turnover.total_completed_round_trips == 1
    assert result.turnover.annual_counts[0].year == 2026
    assert result.performance.start_date == dates[0]
    assert result.performance.end_date == dates[-1]
    assert result.performance.observations == len(dates)
    assert result.backtest.unexecuted_signal_dates == (dates[4],)


def test_weekly_hysteresis_experiment_uses_hold_threshold():
    dates = [
        date(2026, 1, 1),
        date(2026, 1, 2),
        date(2026, 1, 5),
        date(2026, 1, 9),
        date(2026, 1, 12),
    ]
    daily_bars = [
        day(dates[0], {"AAA": ("100", "100"), "BBB": ("100", "100"), "CCC": ("100", "100")}),
        day(dates[1], {"AAA": ("110", "110"), "BBB": ("100", "100"), "CCC": ("100", "100")}),
        day(dates[2], {"AAA": ("112", "112"), "BBB": ("100", "100"), "CCC": ("100", "100")}),
        day(dates[3], {"AAA": ("100", "100"), "BBB": ("120", "120"), "CCC": ("80", "80")}),
        day(dates[4], {"AAA": ("90", "90"), "BBB": ("130", "130"), "CCC": ("100", "100")}),
    ]

    result = run_weekly_hysteresis_momentum_experiment(
        experiment_id="B003",
        daily_bars=daily_bars,
        benchmark_bars=[
            benchmark(dates[0], "1000"),
            benchmark(dates[1], "1005"),
            benchmark(dates[2], "1010"),
            benchmark(dates[3], "1015"),
            benchmark(dates[4], "1020"),
        ],
        universe=["AAA", "BBB", "CCC"],
        starting_cash="10000",
        lookback_sessions=1,
        max_positions=1,
        entry_rank=1,
        hold_rank=2,
        slippage_rate="0",
        complete_years=[2026],
    )

    assert [signal.desired_symbols for signal in result.signals] == [
        ("AAA",),
        ("AAA",),
        ("CCC",),
    ]
    assert [(fill.side, fill.symbol) for fill in result.fills] == [
        (FillSide.BUY, "AAA"),
    ]
    assert result.turnover.total_completed_round_trips == 0


def test_weekly_momentum_experiment_rejects_blank_id():
    with pytest.raises(Phase1ExperimentError, match="experiment_id"):
        run_weekly_momentum_experiment(
            experiment_id=" ",
            daily_bars=[],
            benchmark_bars=[],
            universe=["AAA"],
            starting_cash="10000",
        )


def test_weekly_momentum_experiment_rejects_too_little_data_for_signals():
    only_day = date(2026, 1, 1)

    with pytest.raises(Phase1ExperimentError, match="no weekly momentum signals"):
        run_weekly_momentum_experiment(
            experiment_id="B001",
            daily_bars=[day(only_day, {"AAA": ("100", "100")})],
            benchmark_bars=[benchmark(only_day, "1000")],
            universe=["AAA"],
            starting_cash="10000",
            lookback_sessions=1,
        )


def test_b004_experiment_risk_off_schedules_full_exit_and_no_entries():
    dates = [
        date(2026, 1, 1),
        date(2026, 1, 2),
        date(2026, 1, 5),
        date(2026, 1, 9),
        date(2026, 1, 12),
    ]
    daily_bars = [
        day(dates[0], {"AAA": ("100", "100"), "BBB": ("100", "100")}),
        day(dates[1], {"AAA": ("110", "110"), "BBB": ("100", "100")}),
        day(dates[2], {"AAA": ("110", "110"), "BBB": ("100", "100")}),
        day(dates[3], {"AAA": ("100", "100"), "BBB": ("120", "120")}),
        day(dates[4], {"AAA": ("100", "100"), "BBB": ("120", "130")}),
    ]

    result = run_weekly_regime_filtered_hysteresis_momentum_experiment(
        experiment_id="B004",
        daily_bars=daily_bars,
        benchmark_bars=[
            benchmark(dates[0], "100"),
            benchmark(dates[1], "102"),
            benchmark(dates[2], "100"),
            benchmark(dates[3], "90"),
            benchmark(dates[4], "91"),
        ],
        universe=["AAA", "BBB"],
        starting_cash="10000",
        lookback_sessions=1,
        max_positions=1,
        entry_rank=1,
        hold_rank=2,
        regime_sma_sessions=2,
        slippage_rate="0",
        complete_years=[2026],
    )

    assert [signal.desired_symbols for signal in result.signals] == [
        ("AAA",),
        (),
        ("BBB",),
    ]
    assert [(fill.side, fill.symbol) for fill in result.fills] == [
        (FillSide.BUY, "AAA"),
        (FillSide.SELL, "AAA"),
    ]
    assert result.backtest.final_snapshot.positions == ()
    assert result.regime_exposure is not None
    assert result.regime_exposure.weekly_state_changes == 2


def test_b004_experiment_retries_unfilled_risk_off_exit():
    dates = [
        date(2026, 1, 1),
        date(2026, 1, 2),
        date(2026, 1, 5),
        date(2026, 1, 9),
        date(2026, 1, 12),
        date(2026, 1, 13),
    ]
    daily_bars = [
        day(dates[0], {"AAA": ("100", "100")}),
        day(dates[1], {"AAA": ("110", "110")}),
        day(dates[2], {"AAA": ("110", "110")}),
        day(dates[3], {"AAA": ("100", "100")}),
        day(dates[4], {"AAA": ("100", "100")}),
        day(dates[5], {"AAA": ("100", "100")}),
    ]

    result = run_weekly_regime_filtered_hysteresis_momentum_experiment(
        experiment_id="B004",
        daily_bars=daily_bars,
        benchmark_bars=[
            benchmark(dates[0], "100"),
            benchmark(dates[1], "102"),
            benchmark(dates[2], "100"),
            benchmark(dates[3], "90"),
            benchmark(dates[4], "91"),
            benchmark(dates[5], "92"),
        ],
        universe=["AAA"],
        starting_cash="10000",
        lookback_sessions=1,
        max_positions=1,
        entry_rank=1,
        hold_rank=1,
        regime_sma_sessions=2,
        slippage_rate="0",
        complete_years=[2026],
        untradeable_symbols_by_date={dates[4]: ["AAA"]},
    )

    assert [execution.unfilled_exit_symbols for execution in result.backtest.executions] == [
        (),
        ("AAA",),
        (),
    ]
    assert [(fill.side, fill.symbol) for fill in result.fills] == [
        (FillSide.BUY, "AAA"),
        (FillSide.SELL, "AAA"),
    ]
    assert result.backtest.final_snapshot.positions == ()
