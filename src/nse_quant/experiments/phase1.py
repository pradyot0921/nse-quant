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
from nse_quant.strategies.momentum import MomentumSignal, generate_weekly_momentum_signals


class Phase1ExperimentError(RuntimeError):
    """Raised when a Phase 1 experiment cannot be run."""


@dataclass(frozen=True)
class Phase1ExperimentRun:
    experiment_id: str
    signals: tuple[MomentumSignal, ...]
    backtest: RebalanceLoopResult
    fills: tuple[PortfolioFill, ...]
    execution_costs: tuple[ExecutionCostResult, ...]
    turnover: TurnoverEvaluation
    performance: PerformanceSummary


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

    clean_experiment_id = _experiment_id(experiment_id)
    days = tuple(daily_bars)
    signals = generate_weekly_momentum_signals(
        days,
        universe=universe,
        lookback_sessions=lookback_sessions,
        max_positions=max_positions,
    )
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
    )


def _experiment_id(value: str) -> str:
    experiment_id = value.strip() if isinstance(value, str) else ""
    if not experiment_id:
        raise Phase1ExperimentError("experiment_id must be non-blank")
    return experiment_id
