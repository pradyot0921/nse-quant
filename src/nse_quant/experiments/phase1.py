"""Input-driven Phase 1 experiment runner."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, Mapping

from nse_quant.backtest.data import DailyBars
from nse_quant.backtest.execution import ExecutionCostResult
from nse_quant.backtest.portfolio import PortfolioFill, PortfolioState
from nse_quant.backtest.rebalance_loop import RebalanceLoopResult, run_rebalance_loop
from nse_quant.backtest.turnover import TurnoverEvaluation, evaluate_round_trip_turnover
from nse_quant.data.benchmark import TriBenchmarkBar
from nse_quant.reporting.performance import PerformanceSummary, summarize_performance
from nse_quant.strategies.momentum import (
    FiftyTwoWeekHighInputSummary,
    FiftyTwoWeekHighSignal,
    RegimeExposureSummary,
    RegimeFilteredMomentumSignal,
    MomentumSignal,
    VolatilityExposureSummary,
    VolatilityScaledMomentumSignal,
    generate_weekly_52_week_high_hysteresis_signals,
    generate_weekly_hysteresis_momentum_signals,
    generate_weekly_momentum_signals,
    generate_weekly_regime_filtered_hysteresis_momentum_signals,
    generate_weekly_volatility_scaled_hysteresis_momentum_signals,
    summarize_52_week_high_input,
    summarize_regime_exposure,
    summarize_volatility_exposure,
)


class Phase1ExperimentError(RuntimeError):
    """Raised when a Phase 1 experiment cannot be run."""


@dataclass(frozen=True)
class Phase1ExperimentRun:
    experiment_id: str
    signals: tuple[
        MomentumSignal
        | FiftyTwoWeekHighSignal
        | RegimeFilteredMomentumSignal
        | VolatilityScaledMomentumSignal,
        ...
    ]
    backtest: RebalanceLoopResult
    fills: tuple[PortfolioFill, ...]
    execution_costs: tuple[ExecutionCostResult, ...]
    turnover: TurnoverEvaluation
    performance: PerformanceSummary
    fifty_two_week_high_input: FiftyTwoWeekHighInputSummary | None = None
    regime_exposure: RegimeExposureSummary | None = None
    volatility_exposure: VolatilityExposureSummary | None = None


def run_weekly_momentum_experiment(
    *,
    experiment_id: str,
    daily_bars: Iterable[DailyBars],
    benchmark_bars: Iterable[TriBenchmarkBar],
    universe: Iterable[str],
    starting_cash: Decimal | str | int,
    lookback_sessions: int = 60,
    max_positions: int = 3,
    slippage_rate: Decimal | str | int = Decimal("0.0005"),
    complete_years: Iterable[int] = (),
    annual_turnover_limit: int = 30,
    untradeable_symbols_by_date: Mapping[date, Iterable[str]] | None = None,
) -> Phase1ExperimentRun:
    """Run weekly momentum signals through the existing Phase 1 components."""

    days = tuple(daily_bars)
    signals = generate_weekly_momentum_signals(
        days,
        universe=universe,
        lookback_sessions=lookback_sessions,
        max_positions=max_positions,
    )
    return _run_from_signals(
        experiment_id=experiment_id,
        daily_bars=days,
        benchmark_bars=benchmark_bars,
        signals=signals,
        starting_cash=starting_cash,
        max_positions=max_positions,
        slippage_rate=slippage_rate,
        complete_years=complete_years,
        annual_turnover_limit=annual_turnover_limit,
        untradeable_symbols_by_date=untradeable_symbols_by_date,
    )


def run_weekly_hysteresis_momentum_experiment(
    *,
    experiment_id: str,
    daily_bars: Iterable[DailyBars],
    benchmark_bars: Iterable[TriBenchmarkBar],
    universe: Iterable[str],
    starting_cash: Decimal | str | int,
    lookback_sessions: int = 60,
    max_positions: int = 3,
    entry_rank: int = 3,
    hold_rank: int = 6,
    slippage_rate: Decimal | str | int = Decimal("0.0005"),
    complete_years: Iterable[int] = (),
    annual_turnover_limit: int = 30,
    untradeable_symbols_by_date: Mapping[date, Iterable[str]] | None = None,
) -> Phase1ExperimentRun:
    """Run weekly momentum with pre-registered B003 hysteresis thresholds."""

    days = tuple(daily_bars)
    signals = generate_weekly_hysteresis_momentum_signals(
        days,
        universe=universe,
        lookback_sessions=lookback_sessions,
        max_positions=max_positions,
        entry_rank=entry_rank,
        hold_rank=hold_rank,
    )
    return _run_from_signals(
        experiment_id=experiment_id,
        daily_bars=days,
        benchmark_bars=benchmark_bars,
        signals=signals,
        starting_cash=starting_cash,
        max_positions=max_positions,
        slippage_rate=slippage_rate,
        complete_years=complete_years,
        annual_turnover_limit=annual_turnover_limit,
        untradeable_symbols_by_date=untradeable_symbols_by_date,
    )


def run_weekly_regime_filtered_hysteresis_momentum_experiment(
    *,
    experiment_id: str,
    daily_bars: Iterable[DailyBars],
    benchmark_bars: Iterable[TriBenchmarkBar],
    universe: Iterable[str],
    starting_cash: Decimal | str | int,
    lookback_sessions: int = 60,
    max_positions: int = 3,
    entry_rank: int = 3,
    hold_rank: int = 6,
    regime_sma_sessions: int = 200,
    slippage_rate: Decimal | str | int = Decimal("0.0005"),
    complete_years: Iterable[int] = (),
    annual_turnover_limit: int = 30,
    untradeable_symbols_by_date: Mapping[date, Iterable[str]] | None = None,
) -> Phase1ExperimentRun:
    """Run the frozen B004 regime-filtered B003 structure."""

    days = tuple(daily_bars)
    benchmark_tuple = tuple(benchmark_bars)
    signals = generate_weekly_regime_filtered_hysteresis_momentum_signals(
        days,
        benchmark_bars=benchmark_tuple,
        universe=universe,
        lookback_sessions=lookback_sessions,
        max_positions=max_positions,
        entry_rank=entry_rank,
        hold_rank=hold_rank,
        regime_sma_sessions=regime_sma_sessions,
    )
    return _run_from_signals(
        experiment_id=experiment_id,
        daily_bars=days,
        benchmark_bars=benchmark_tuple,
        signals=signals,
        starting_cash=starting_cash,
        max_positions=max_positions,
        slippage_rate=slippage_rate,
        complete_years=complete_years,
        annual_turnover_limit=annual_turnover_limit,
        untradeable_symbols_by_date=untradeable_symbols_by_date,
        regime_exposure=summarize_regime_exposure(
            days,
            benchmark_bars=benchmark_tuple,
            weekly_signals=signals,
            regime_sma_sessions=regime_sma_sessions,
        ),
    )


def run_weekly_52_week_high_proximity_experiment(
    *,
    experiment_id: str,
    daily_bars: Iterable[DailyBars],
    benchmark_bars: Iterable[TriBenchmarkBar],
    universe: Iterable[str],
    starting_cash: Decimal | str | int,
    performance_start_date: date,
    performance_end_date: date,
    high_window_calendar_days: int = 364,
    max_positions: int = 3,
    entry_rank: int = 3,
    hold_rank: int = 6,
    slippage_rate: Decimal | str | int = Decimal("0.0005"),
    complete_years: Iterable[int] = (),
    annual_turnover_limit: int = 30,
    untradeable_symbols_by_date: Mapping[date, Iterable[str]] | None = None,
) -> Phase1ExperimentRun:
    """Run the frozen B006 52-week-high proximity ranking structure."""

    days = tuple(sorted(daily_bars, key=lambda item: item.trade_date))
    performance_days = tuple(
        day
        for day in days
        if performance_start_date <= day.trade_date <= performance_end_date
    )
    performance_dates = {day.trade_date for day in performance_days}
    signals = tuple(
        signal
        for signal in generate_weekly_52_week_high_hysteresis_signals(
            days,
            universe=universe,
            high_window_calendar_days=high_window_calendar_days,
            max_positions=max_positions,
            entry_rank=entry_rank,
            hold_rank=hold_rank,
            require_full_window_from=performance_start_date,
        )
        if signal.signal_date in performance_dates
    )
    return _run_from_signals(
        experiment_id=experiment_id,
        daily_bars=performance_days,
        benchmark_bars=benchmark_bars,
        signals=signals,
        starting_cash=starting_cash,
        max_positions=max_positions,
        slippage_rate=slippage_rate,
        complete_years=complete_years,
        annual_turnover_limit=annual_turnover_limit,
        untradeable_symbols_by_date=untradeable_symbols_by_date,
        fifty_two_week_high_input=summarize_52_week_high_input(
            signals,
            high_window_calendar_days=high_window_calendar_days,
        ),
    )


def run_weekly_volatility_scaled_hysteresis_momentum_experiment(
    *,
    experiment_id: str,
    daily_bars: Iterable[DailyBars],
    benchmark_bars: Iterable[TriBenchmarkBar],
    universe: Iterable[str],
    starting_cash: Decimal | str | int,
    lookback_sessions: int = 60,
    max_positions: int = 3,
    entry_rank: int = 3,
    hold_rank: int = 6,
    volatility_lookback_sessions: int = 126,
    target_volatility: Decimal | str | int = Decimal("0.12"),
    slippage_rate: Decimal | str | int = Decimal("0.0005"),
    complete_years: Iterable[int] = (),
    annual_turnover_limit: int = 30,
    untradeable_symbols_by_date: Mapping[date, Iterable[str]] | None = None,
) -> Phase1ExperimentRun:
    """Run the frozen B005 volatility-scaled B003 structure."""

    days = tuple(daily_bars)
    benchmark_tuple = tuple(benchmark_bars)
    universe_tuple = tuple(universe)
    reference_signals = generate_weekly_hysteresis_momentum_signals(
        days,
        universe=universe_tuple,
        lookback_sessions=lookback_sessions,
        max_positions=max_positions,
        entry_rank=entry_rank,
        hold_rank=hold_rank,
    )
    reference_backtest = run_rebalance_loop(
        days,
        starting_state=PortfolioState.starting_cash(starting_cash),
        desired_symbols_by_signal_date={
            signal.signal_date: signal.desired_symbols
            for signal in reference_signals
        },
        max_positions=max_positions,
        slippage_rate=slippage_rate,
        untradeable_symbols_by_date=untradeable_symbols_by_date,
    )
    signals = generate_weekly_volatility_scaled_hysteresis_momentum_signals(
        days,
        reference_nav_by_date={
            snapshot.trade_date: snapshot.nav
            for snapshot in reference_backtest.snapshots
        },
        universe=universe_tuple,
        lookback_sessions=lookback_sessions,
        max_positions=max_positions,
        entry_rank=entry_rank,
        hold_rank=hold_rank,
        volatility_lookback_sessions=volatility_lookback_sessions,
        target_volatility=target_volatility,
    )
    return _run_from_signals(
        experiment_id=experiment_id,
        daily_bars=days,
        benchmark_bars=benchmark_tuple,
        signals=signals,
        starting_cash=starting_cash,
        max_positions=max_positions,
        slippage_rate=slippage_rate,
        complete_years=complete_years,
        annual_turnover_limit=annual_turnover_limit,
        untradeable_symbols_by_date=untradeable_symbols_by_date,
        target_exposure_by_signal_date={
            signal.signal_date: signal.exposure_multiplier
            for signal in signals
        },
        volatility_exposure=summarize_volatility_exposure(
            days,
            weekly_signals=signals,
            volatility_lookback_sessions=volatility_lookback_sessions,
            target_volatility=target_volatility,
        ),
    )


def _run_from_signals(
    *,
    experiment_id: str,
    daily_bars: Iterable[DailyBars],
    benchmark_bars: Iterable[TriBenchmarkBar],
    signals: tuple[
        MomentumSignal
        | FiftyTwoWeekHighSignal
        | RegimeFilteredMomentumSignal
        | VolatilityScaledMomentumSignal,
        ...
    ],
    starting_cash: Decimal | str | int,
    max_positions: int,
    slippage_rate: Decimal | str | int,
    complete_years: Iterable[int],
    annual_turnover_limit: int,
    untradeable_symbols_by_date: Mapping[date, Iterable[str]] | None,
    target_exposure_by_signal_date: Mapping[date, Decimal] | None = None,
    fifty_two_week_high_input: FiftyTwoWeekHighInputSummary | None = None,
    regime_exposure: RegimeExposureSummary | None = None,
    volatility_exposure: VolatilityExposureSummary | None = None,
) -> Phase1ExperimentRun:
    clean_experiment_id = _experiment_id(experiment_id)
    days = tuple(daily_bars)
    if not signals:
        raise Phase1ExperimentError("no weekly momentum signals generated")

    backtest = run_rebalance_loop(
        days,
        starting_state=PortfolioState.starting_cash(starting_cash),
        desired_symbols_by_signal_date={
            signal.signal_date: signal.desired_symbols for signal in signals
        },
        max_positions=max_positions,
        slippage_rate=slippage_rate,
        target_exposure_by_signal_date=target_exposure_by_signal_date,
        untradeable_symbols_by_date=untradeable_symbols_by_date,
    )
    fills = tuple(
        fill
        for execution in backtest.executions
        for fill in execution.costs.portfolio_fills
    )
    execution_costs = tuple(execution.costs for execution in backtest.executions)
    turnover = evaluate_round_trip_turnover(
        fills,
        complete_years=complete_years,
        annual_limit=annual_turnover_limit,
    )
    performance = summarize_performance(backtest.snapshots, benchmark_bars)

    return Phase1ExperimentRun(
        experiment_id=clean_experiment_id,
        signals=signals,
        backtest=backtest,
        fills=fills,
        execution_costs=execution_costs,
        turnover=turnover,
        performance=performance,
        fifty_two_week_high_input=fifty_two_week_high_input,
        regime_exposure=regime_exposure,
        volatility_exposure=volatility_exposure,
    )


def _experiment_id(value: str) -> str:
    experiment_id = value.strip() if isinstance(value, str) else ""
    if not experiment_id:
        raise Phase1ExperimentError("experiment_id must be non-blank")
    return experiment_id
