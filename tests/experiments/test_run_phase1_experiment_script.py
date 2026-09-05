from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import importlib.util

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_phase1_experiment.py"


def load_script():
    spec = importlib.util.spec_from_file_location("run_phase1_experiment", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_run_phase1_experiment_script_writes_report_and_trade_log(tmp_path):
    script = load_script()
    ledger = tmp_path / "ledger.csv"
    universe = tmp_path / "universe.csv"
    dataset = tmp_path / "dataset.csv"
    benchmark = tmp_path / "benchmark.csv"
    output_dir = tmp_path / "results"
    sessions = _weekday_sessions(date(2016, 1, 1), 65)

    ledger.write_text(
        "\n".join(
            [
                "experiment_id,strategy,universe_version,data_version,research_period,validation_period",
                (
                    "B001,3-position weekly relative-momentum baseline,u_v0,d_v0,"
                    f"{sessions[0]}..{sessions[-1]},2016-04-01..2016-04-04"
                ),
            ]
        ),
        encoding="utf-8",
    )
    universe.write_text("symbol\nAAA\nBBB\n", encoding="utf-8")
    dataset.write_text(
        _dataset_csv(sessions),
        encoding="utf-8",
    )
    benchmark.write_text(
        _benchmark_csv(sessions),
        encoding="utf-8",
    )

    exit_code = script.main(
        [
            "--experiment-id",
            "B001",
            "--period",
            "research",
            "--ledger",
            str(ledger),
            "--universe",
            str(universe),
            "--dataset",
            str(dataset),
            "--benchmark",
            str(benchmark),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    report = output_dir / "B001_research" / "phase1_report.md"
    trade_log = output_dir / "B001_research" / "trade_log.csv"
    assert "| Experiment | `B001` |" in report.read_text(encoding="utf-8")
    assert "| Universe version | `u_v0` |" in report.read_text(encoding="utf-8")
    assert "AAA,BUY" in trade_log.read_text(encoding="utf-8")
    assert "BBB,BUY" in trade_log.read_text(encoding="utf-8")


def test_run_phase1_experiment_script_supports_b003_hysteresis(tmp_path):
    script = load_script()
    ledger = tmp_path / "ledger.csv"
    universe = tmp_path / "universe.csv"
    dataset = tmp_path / "dataset.csv"
    benchmark = tmp_path / "benchmark.csv"
    output_dir = tmp_path / "results"
    sessions = _weekday_sessions(date(2016, 1, 1), 65)

    ledger.write_text(
        "\n".join(
            [
                "experiment_id,strategy,universe_version,data_version,research_period,validation_period",
                (
                    "B003,weekly momentum with hysteresis,u_v0,d_v0,"
                    f"{sessions[0]}..{sessions[-1]},2016-04-01..2016-04-04"
                ),
            ]
        ),
        encoding="utf-8",
    )
    universe.write_text("symbol\nAAA\nBBB\n", encoding="utf-8")
    dataset.write_text(_dataset_csv(sessions), encoding="utf-8")
    benchmark.write_text(_benchmark_csv(sessions), encoding="utf-8")

    exit_code = script.main(
        [
            "--experiment-id",
            "B003",
            "--period",
            "research",
            "--ledger",
            str(ledger),
            "--universe",
            str(universe),
            "--dataset",
            str(dataset),
            "--benchmark",
            str(benchmark),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    report = output_dir / "B003_research" / "phase1_report.md"
    assert "| Experiment | `B003` |" in report.read_text(encoding="utf-8")


def test_run_phase1_experiment_script_supports_b004_research_only(tmp_path):
    script = load_script()
    ledger = tmp_path / "ledger.csv"
    universe = tmp_path / "universe.csv"
    dataset = tmp_path / "dataset.csv"
    benchmark = tmp_path / "benchmark.csv"
    output_dir = tmp_path / "results"
    sessions = _weekday_sessions(date(2016, 1, 1), 205)

    ledger.write_text(
        "\n".join(
            [
                "experiment_id,strategy,universe_version,data_version,research_period,validation_period,slippage_model",
                (
                    "B004,weekly relative momentum with hysteresis + exogenous Nifty 100 TRI SMA200 regime filter,u_v0,d_v0,"
                    f"{sessions[0]}..{sessions[-1]},2017-01-01..2017-01-10,adverse deterministic slippage 0.05% baseline"
                ),
            ]
        ),
        encoding="utf-8",
    )
    universe.write_text("symbol\nAAA\nBBB\n", encoding="utf-8")
    dataset.write_text(_dataset_csv(sessions), encoding="utf-8")
    benchmark.write_text(_benchmark_csv(sessions), encoding="utf-8")

    exit_code = script.main(
        [
            "--experiment-id",
            "B004",
            "--period",
            "research",
            "--ledger",
            str(ledger),
            "--universe",
            str(universe),
            "--dataset",
            str(dataset),
            "--benchmark",
            str(benchmark),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    report = output_dir / "B004_research" / "phase1_report.md"
    text = report.read_text(encoding="utf-8")
    assert "| Experiment | `B004` |" in text
    assert "## Market Regime" in text
    assert "| Regime unavailable sessions | 199 |" in text
    assert "## Direct Candidate Comparison" in text
    assert "| CAGR |" in text
    assert "| Maximum drawdown |" in text
    assert "| Sharpe |" in text
    assert "| Transaction costs |" in text
    assert "| Percentage time invested |" in text


def test_run_phase1_experiment_script_blocks_b004_validation(tmp_path):
    script = load_script()
    ledger = tmp_path / "ledger.csv"
    ledger.write_text(
        "\n".join(
            [
                "experiment_id,strategy,universe_version,data_version,research_period,validation_period",
                "B004,weekly relative momentum with hysteresis + filter,u_v0,d_v0,2016-01-01..2016-01-31,2023-01-01..2023-01-31",
            ]
        ),
        encoding="utf-8",
    )

    try:
        script.main(["--experiment-id", "B004", "--period", "validation", "--ledger", str(ledger)])
    except SystemExit as exc:
        assert "validation run is blocked until a Phase 3 promotion artifact exists" in str(exc)
    else:
        raise AssertionError("B004 validation run was not blocked")


def test_run_phase1_experiment_script_supports_b005_research_only(tmp_path):
    script = load_script()
    ledger = tmp_path / "ledger.csv"
    universe = tmp_path / "universe.csv"
    dataset = tmp_path / "dataset.csv"
    benchmark = tmp_path / "benchmark.csv"
    output_dir = tmp_path / "results"
    sessions = _weekday_sessions(date(2016, 1, 1), 135)

    ledger.write_text(
        "\n".join(
            [
                "experiment_id,strategy,universe_version,data_version,research_period,validation_period,slippage_model",
                (
                    "B005,weekly relative momentum with hysteresis + realized-volatility exposure scaling,u_v0,d_v0,"
                    f"{sessions[0]}..{sessions[-1]},2017-01-01..2017-01-10,adverse deterministic slippage 0.05% baseline"
                ),
            ]
        ),
        encoding="utf-8",
    )
    universe.write_text("symbol\nAAA\nBBB\n", encoding="utf-8")
    dataset.write_text(_dataset_csv(sessions), encoding="utf-8")
    benchmark.write_text(_benchmark_csv(sessions), encoding="utf-8")

    exit_code = script.main(
        [
            "--experiment-id",
            "B005",
            "--period",
            "research",
            "--ledger",
            str(ledger),
            "--universe",
            str(universe),
            "--dataset",
            str(dataset),
            "--benchmark",
            str(benchmark),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    report = output_dir / "B005_research" / "phase1_report.md"
    text = report.read_text(encoding="utf-8")
    assert "| Experiment | `B005` |" in text
    assert "## Volatility Exposure" in text
    assert "| Realized-volatility lookback sessions | 126 |" in text
    assert "| Target volatility | 0.120000 |" in text
    assert "## Direct Candidate Comparison" in text
    assert "| CAGR |" in text
    assert "REALIZED-VOLATILITY LIMITATION:" in text


def test_run_phase1_experiment_script_blocks_b005_validation(tmp_path):
    script = load_script()
    ledger = tmp_path / "ledger.csv"
    ledger.write_text(
        "\n".join(
            [
                "experiment_id,strategy,universe_version,data_version,research_period,validation_period",
                "B005,weekly relative momentum with hysteresis + volatility scaling,u_v0,d_v0,2016-01-01..2016-01-31,2023-01-01..2023-01-31",
            ]
        ),
        encoding="utf-8",
    )

    try:
        script.main(["--experiment-id", "B005", "--period", "validation", "--ledger", str(ledger)])
    except SystemExit as exc:
        assert "validation run is blocked until a Phase 3 promotion artifact exists" in str(exc)
    else:
        raise AssertionError("B005 validation run was not blocked")


def test_run_phase1_experiment_script_supports_b006_research_only_with_warmup(tmp_path):
    script = load_script()
    ledger = tmp_path / "ledger.csv"
    universe = tmp_path / "universe.csv"
    dataset = tmp_path / "dataset.csv"
    benchmark = tmp_path / "benchmark.csv"
    output_dir = tmp_path / "results"
    sessions = _weekday_sessions(date(2015, 1, 1), 270)
    research_sessions = [session for session in sessions if session >= date(2016, 1, 1)]

    ledger.write_text(
        "\n".join(
            [
                "experiment_id,strategy,universe_version,data_version,research_period,validation_period,slippage_model",
                (
                    "B006,weekly 52-week-high proximity ranking with hysteresis,"
                    "u_v0,nifty100_v0_52w_high_input_warmup_d074,"
                    f"{research_sessions[0]}..{research_sessions[-1]},"
                    "2017-01-01..2017-01-10,"
                    "adverse deterministic slippage 0.05% baseline"
                ),
            ]
        ),
        encoding="utf-8",
    )
    universe.write_text("symbol\nAAA\nBBB\n", encoding="utf-8")
    dataset.write_text(_dataset_csv(sessions), encoding="utf-8")
    benchmark.write_text(_benchmark_csv(research_sessions), encoding="utf-8")

    exit_code = script.main(
        [
            "--experiment-id",
            "B006",
            "--period",
            "research",
            "--ledger",
            str(ledger),
            "--universe",
            str(universe),
            "--dataset",
            str(dataset),
            "--benchmark",
            str(benchmark),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    report = output_dir / "B006_research" / "phase1_report.md"
    text = report.read_text(encoding="utf-8")
    assert "| Experiment | `B006` |" in text
    assert "## 52-Week-High Signal" in text
    assert "| Lookback calendar days | 364 |" in text
    assert "| Missing or invalid PH52 scores | 0 |" in text
    assert "52-WEEK-HIGH LIMITATION:" in text
    assert "## Direct Candidate Comparison" in text


def test_run_phase1_experiment_script_blocks_b006_validation(tmp_path):
    script = load_script()
    ledger = tmp_path / "ledger.csv"
    ledger.write_text(
        "\n".join(
            [
                "experiment_id,strategy,universe_version,data_version,research_period,validation_period",
                "B006,weekly 52-week-high proximity ranking with hysteresis,u_v0,d_v0,2016-01-01..2016-01-31,2023-01-01..2023-01-31",
            ]
        ),
        encoding="utf-8",
    )

    try:
        script.main(["--experiment-id", "B006", "--period", "validation", "--ledger", str(ledger)])
    except SystemExit as exc:
        assert "validation run is blocked until a Phase 3 promotion artifact exists" in str(exc)
    else:
        raise AssertionError("B006 validation run was not blocked")


@pytest.mark.parametrize(
    ("experiment_id", "status"),
    [("B006", "CANCELLED"), ("B006-S015", "NOT_RUN")],
)
def test_run_phase1_experiment_script_blocks_cancelled_b006_research(
    tmp_path, experiment_id, status
):
    script = load_script()
    ledger = tmp_path / "ledger.csv"
    ledger.write_text(
        "\n".join(
            [
                "experiment_id,status,strategy,universe_version,data_version,research_period,validation_period",
                f"{experiment_id},{status},weekly 52-week-high proximity ranking with hysteresis,u_v0,d_v0,2016-01-01..2016-01-31,2023-01-01..2023-01-31",
            ]
        ),
        encoding="utf-8",
    )

    try:
        script.main(["--experiment-id", experiment_id, "--period", "research", "--ledger", str(ledger)])
    except SystemExit as exc:
        assert "warm-up dataset readiness failed" in str(exc)
    else:
        raise AssertionError("cancelled B006 research run was not blocked")


def _weekday_sessions(start: date, count: int) -> list[date]:
    sessions = []
    current = start
    while len(sessions) < count:
        if current.weekday() < 5:
            sessions.append(current)
        current += timedelta(days=1)
    return sessions


def _dataset_csv(sessions: list[date]) -> str:
    lines = [
        "trade_date,symbol,adjusted_open,adjusted_high,adjusted_low,adjusted_close,adjusted_volume,raw_traded_value"
    ]
    for index, session in enumerate(sessions):
        aaa = 100 + index
        bbb = 100 + index * 2
        lines.append(f"{session},AAA,{aaa},{aaa},{aaa},{aaa},1000,100000")
        lines.append(f"{session},BBB,{bbb},{bbb},{bbb},{bbb},1000,100000")
    return "\n".join(lines)


def _benchmark_csv(sessions: list[date]) -> str:
    lines = ["trade_date,index_name,total_return_index,net_total_return_index"]
    for index, session in enumerate(sessions):
        lines.append(f"{session},Nifty 100,{1000 + index},")
    return "\n".join(lines)
