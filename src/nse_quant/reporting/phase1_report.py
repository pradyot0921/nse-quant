"""Markdown report writer for Phase 1 experiment summaries."""

from __future__ import annotations

from pathlib import Path
from decimal import Decimal
from typing import Iterable

from nse_quant.backtest.execution import ExecutionCostResult
from nse_quant.backtest.turnover import TurnoverEvaluation
from nse_quant.reporting.performance import PerformanceSummary


DEFAULT_RESEARCH_WARNINGS = (
    "SURVIVORSHIP-BIASED V0 UNIVERSE",
    "NOT POINT-IN-TIME",
    "NOT LIVE-TRADING VALIDATION",
    "SMALL SAMPLE: 20 STOCKS / 2-3 POSITIONS / ONE FIXED UNIVERSE",
    "FEW INDEPENDENT BETS - ESTIMATES HAVE WIDE ERROR BARS",
    "CURRENT 2026 COST SCHEDULE APPLIED RETROSPECTIVELY",
    "UNSUPPORTED-CORPORATE-ACTION FILTER APPLIED",
)


def write_phase1_markdown_report(
    output_path: str | Path,
    *,
    experiment_id: str,
    strategy_name: str,
    universe_version: str,
    data_version: str,
    performance: PerformanceSummary,
    turnover: TurnoverEvaluation,
    execution_costs: Iterable[ExecutionCostResult] = (),
    warnings: Iterable[str] = DEFAULT_RESEARCH_WARNINGS,
    notes: Iterable[str] = (),
) -> Path:
    """Write a deterministic Markdown summary for one Phase 1 experiment."""

    output = Path(output_path)
    total_costs = _total_costs(execution_costs)
    drawdown_status = "PASS" if performance.drawdown_gate_passed else "FAIL"
    turnover_status = "PASS" if turnover.passed else "FAIL"

    lines = [
        f"# Phase 1 Experiment Report - {experiment_id}",
        "",
        "## Identity",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Experiment | `{experiment_id}` |",
        f"| Strategy | {strategy_name} |",
        f"| Universe version | `{universe_version}` |",
        f"| Data version | `{data_version}` |",
        f"| Period | `{performance.start_date}` to `{performance.end_date}` |",
        f"| Observations | {performance.observations} |",
        "",
        "## Portfolio",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Starting capital | {performance.strategy_start_nav} |",
        f"| Ending capital | {performance.strategy_end_nav} |",
        f"| Net return | {performance.strategy_total_return} |",
        f"| CAGR | {performance.strategy_cagr} |",
        f"| Volatility | {performance.strategy_annualized_volatility} |",
        f"| Maximum drawdown | {performance.strategy_max_drawdown} |",
        f"| Transaction costs | {total_costs} |",
        f"| Completed round trips | {turnover.total_completed_round_trips} |",
        f"| Turnover | {turnover.total_turnover} |",
        f"| Turnover gate | {turnover_status} |",
        "",
        "## Benchmark",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Benchmark start TRI | {performance.benchmark_start_tri} |",
        f"| Benchmark end TRI | {performance.benchmark_end_tri} |",
        f"| Benchmark return | {performance.benchmark_total_return} |",
        f"| Benchmark CAGR | {performance.benchmark_cagr} |",
        f"| Benchmark volatility | {performance.benchmark_annualized_volatility} |",
        f"| Benchmark maximum drawdown | {performance.benchmark_max_drawdown} |",
        "",
        "## Relative",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| CAGR difference | {performance.strategy_cagr - performance.benchmark_cagr} |",
        f"| Drawdown difference | {performance.strategy_max_drawdown - performance.benchmark_max_drawdown} |",
        f"| Drawdown gate | {drawdown_status} |",
        "",
        "## Research Warnings",
        "",
    ]
    lines.extend(f"- {warning}" for warning in tuple(warnings))
    lines.extend(["", "## Notes", ""])
    note_tuple = tuple(notes)
    if note_tuple:
        lines.extend(f"- {note}" for note in note_tuple)
    else:
        lines.append("None.")
    lines.append("")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def _total_costs(execution_costs: Iterable[ExecutionCostResult]) -> Decimal:
    return sum((execution.total_cost for execution in execution_costs), Decimal("0.00"))
