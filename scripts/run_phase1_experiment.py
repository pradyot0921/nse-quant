from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import argparse
import csv

from nse_quant.backtest.data import group_bars_by_date, load_processed_backtest_bars
from nse_quant.data.benchmark import load_tri_benchmark_csv
from nse_quant.data.processed_dataset import load_universe_symbols
from nse_quant.experiments.phase1 import (
    run_weekly_hysteresis_momentum_experiment,
    run_weekly_momentum_experiment,
    run_weekly_regime_filtered_hysteresis_momentum_experiment,
)
from nse_quant.reporting.phase1_report import write_phase1_markdown_report
from nse_quant.reporting.trade_log import (
    trade_log_rows_from_execution,
    write_trade_log_csv,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = PROJECT_ROOT / "experiments" / "ledger.csv"
DEFAULT_UNIVERSE = PROJECT_ROOT / "universes" / "nifty100_v0_20.csv"
DEFAULT_DATASET = PROJECT_ROOT / "data" / "processed" / "nifty100_v0_adjusted_ohlcv.csv"
DEFAULT_BENCHMARK = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "benchmarks"
    / "nifty100_tri_2016-01-01_2026-08-19.csv"
)
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "experiments" / "results"
B003_BASELINE_COMPARISON = {
    "CAGR": "0.136461",
    "Maximum drawdown": "0.512654",
    "Sharpe": "0.636888",
    "Completed round trips": "124",
    "Transaction costs": "10344.51",
    "Percentage time invested": "0.964079",
}
SUPPORTED_EXPERIMENTS = {
    "B001": {"kind": "momentum", "max_positions": 3, "slippage_rate": "0.0005"},
    "B001-S015": {"kind": "momentum", "max_positions": 3, "slippage_rate": "0.0015"},
    "B002": {"kind": "momentum", "max_positions": 2, "slippage_rate": "0.0005"},
    "B002-S015": {"kind": "momentum", "max_positions": 2, "slippage_rate": "0.0015"},
    "B003": {
        "kind": "hysteresis",
        "max_positions": 3,
        "slippage_rate": "0.0005",
        "entry_rank": 3,
        "hold_rank": 6,
    },
    "B003-S015": {
        "kind": "hysteresis",
        "max_positions": 3,
        "slippage_rate": "0.0015",
        "entry_rank": 3,
        "hold_rank": 6,
    },
    "B004": {
        "kind": "regime_hysteresis",
        "max_positions": 3,
        "slippage_rate": "0.0005",
        "entry_rank": 3,
        "hold_rank": 6,
        "regime_sma_sessions": 200,
    },
    "B004-S015": {
        "kind": "regime_hysteresis",
        "max_positions": 3,
        "slippage_rate": "0.0015",
        "entry_rank": 3,
        "hold_rank": 6,
        "regime_sma_sessions": 200,
    },
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--period", choices=("research", "validation"), required=True)
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    parser.add_argument("--universe", default=str(DEFAULT_UNIVERSE))
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET))
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args(argv)

    experiment_id = args.experiment_id.strip().upper()
    if experiment_id not in SUPPORTED_EXPERIMENTS:
        raise SystemExit(f"{experiment_id} is not supported by this runner")
    if args.period == "validation" and experiment_id in {"B004", "B004-S015"}:
        raise SystemExit(
            f"{experiment_id} validation run is blocked until a Phase 3 "
            "promotion artifact exists"
        )

    ledger_row = _ledger_row(Path(args.ledger), experiment_id)
    start_date, end_date = _period_dates(ledger_row, args.period)
    bars = tuple(
        bar
        for bar in load_processed_backtest_bars(args.dataset)
        if start_date <= bar.trade_date <= end_date
    )
    benchmark_bars = tuple(
        bar
        for bar in load_tri_benchmark_csv(args.benchmark)
        if start_date <= bar.trade_date <= end_date
    )

    config = SUPPORTED_EXPERIMENTS[experiment_id]
    result = _run_experiment(
        config=config,
        experiment_id=experiment_id,
        daily_bars=group_bars_by_date(bars),
        benchmark_bars=benchmark_bars,
        universe=load_universe_symbols(args.universe),
        complete_years=_complete_years(start_date, end_date),
    )

    run_dir = Path(args.output_dir) / f"{experiment_id}_{args.period}"
    report_path = write_phase1_markdown_report(
        run_dir / "phase1_report.md",
        experiment_id=experiment_id,
        strategy_name=ledger_row["strategy"],
        universe_version=ledger_row["universe_version"],
        data_version=ledger_row["data_version"],
        performance=result.performance,
        turnover=result.turnover,
        execution_costs=result.execution_costs,
        fills=result.fills,
        portfolio_snapshots=result.backtest.snapshots,
        slippage_model=_slippage_model(ledger_row, config),
        complete_years=_complete_years(start_date, end_date),
        comparison_rows=_comparison_rows(experiment_id, result),
        notes=(
            f"Period: {args.period}",
            "Generated by scripts/run_phase1_experiment.py.",
            "Ledger result fields are not updated by this script.",
        ),
        regime_exposure=result.regime_exposure,
    )
    trade_rows = tuple(
        row
        for execution_costs in result.execution_costs
        for row in trade_log_rows_from_execution(execution_costs)
    )
    trade_log_path = write_trade_log_csv(trade_rows, run_dir / "trade_log.csv")

    print(f"Wrote {report_path}")
    print(f"Wrote {trade_log_path}")
    print(f"experiment_id={result.experiment_id}")
    print(f"period={args.period}")
    print(f"signals={len(result.signals)}")
    print(f"executions={len(result.backtest.executions)}")
    print(f"fills={len(result.fills)}")
    print(f"completed_round_trips={result.turnover.total_completed_round_trips}")
    print(f"turnover_gate={'PASS' if result.turnover.passed else 'FAIL'}")
    print(
        f"drawdown_gate="
        f"{'PASS' if result.performance.drawdown_gate_passed else 'FAIL'}"
    )
    return 0


def _run_experiment(
    *,
    config: dict[str, object],
    experiment_id: str,
    daily_bars,
    benchmark_bars,
    universe,
    complete_years: tuple[int, ...],
):
    common = {
        "experiment_id": experiment_id,
        "daily_bars": daily_bars,
        "benchmark_bars": benchmark_bars,
        "universe": universe,
        "starting_cash": "50000",
        "lookback_sessions": 60,
        "max_positions": int(config["max_positions"]),
        "slippage_rate": str(config["slippage_rate"]),
        "complete_years": complete_years,
    }
    if config["kind"] == "hysteresis":
        return run_weekly_hysteresis_momentum_experiment(
            **common,
            entry_rank=int(config["entry_rank"]),
            hold_rank=int(config["hold_rank"]),
        )
    if config["kind"] == "regime_hysteresis":
        return run_weekly_regime_filtered_hysteresis_momentum_experiment(
            **common,
            entry_rank=int(config["entry_rank"]),
            hold_rank=int(config["hold_rank"]),
            regime_sma_sessions=int(config["regime_sma_sessions"]),
        )
    return run_weekly_momentum_experiment(**common)


def _ledger_row(path: Path, experiment_id: str) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    for row in rows:
        if row["experiment_id"].strip().upper() == experiment_id:
            return row
    raise SystemExit(f"experiment {experiment_id} was not found in {path}")


def _slippage_model(row: dict[str, str], config: dict[str, object]) -> str:
    ledger_value = row.get("slippage_model", "").strip()
    if ledger_value:
        return ledger_value
    return f"adverse deterministic slippage {config['slippage_rate']}"


def _comparison_rows(experiment_id, result) -> tuple[tuple[str, str, str], ...]:
    if experiment_id != "B004":
        return ()
    current = {
        "CAGR": str(result.performance.strategy_cagr),
        "Maximum drawdown": str(result.performance.strategy_max_drawdown),
        "Sharpe": str(result.performance.strategy_sharpe),
        "Completed round trips": str(result.turnover.total_completed_round_trips),
        "Transaction costs": str(
            sum(
                (execution.total_cost for execution in result.execution_costs),
                Decimal("0.00"),
            )
        ),
        "Percentage time invested": _time_invested(result.backtest.snapshots),
    }
    return tuple(
        (metric, current[metric], B003_BASELINE_COMPARISON[metric])
        for metric in B003_BASELINE_COMPARISON
    )


def _time_invested(snapshots) -> str:
    snapshot_tuple = tuple(snapshots)
    if not snapshot_tuple:
        return "N/A"
    invested = sum(1 for snapshot in snapshot_tuple if snapshot.positions)
    value = Decimal(invested) / Decimal(len(snapshot_tuple))
    return str(value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))


def _period_dates(row: dict[str, str], period: str) -> tuple[date, date]:
    field = "research_period" if period == "research" else "validation_period"
    try:
        start_text, end_text = row[field].split("..", 1)
    except ValueError:
        raise SystemExit(f"{field} must use START..END format") from None
    return date.fromisoformat(start_text), date.fromisoformat(end_text)


def _complete_years(start_date: date, end_date: date) -> tuple[int, ...]:
    years = []
    for year in range(start_date.year, end_date.year + 1):
        if date(year, 1, 1) >= start_date and date(year, 12, 31) <= end_date:
            years.append(year)
    return tuple(years)


if __name__ == "__main__":
    raise SystemExit(main())
