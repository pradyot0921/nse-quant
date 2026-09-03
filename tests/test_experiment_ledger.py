import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "experiments" / "ledger.csv"


def rows():
    with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        return tuple(csv.DictReader(handle))


def test_experiment_ledger_references_frozen_universe_and_dataset_versions():
    expected_ids = {
        "B001",
        "B001-S015",
        "B002",
        "B002-S015",
        "B003",
        "B003-S015",
        "B004",
        "B004-S015",
    }
    ledger_rows = rows()
    status_by_id = {row["experiment_id"]: row["status"] for row in ledger_rows}

    assert {row["experiment_id"] for row in ledger_rows} == expected_ids
    assert status_by_id["B001"] == "REJECTED"
    assert status_by_id["B002"] == "REJECTED"
    assert status_by_id["B003"] == "REJECTED"
    for row in ledger_rows:
        if row["experiment_id"] not in {"B001", "B002", "B003"}:
            assert row["status"] == "PLANNED"
        assert row["universe_version"] == "nifty100_v0_20_d037"
        assert row["data_version"] == "nifty100_v0_adjusted_ohlcv_d039"
        assert "pending" not in row["universe_version"].lower()
        assert "pending" not in row["data_version"].lower()


def test_phase1_ledger_records_b001_research_result_only():
    ledger_rows = rows()
    by_id = {row["experiment_id"]: row for row in ledger_rows}
    b001 = by_id["B001"]

    assert b001["cagr"] == "0.173960"
    assert b001["max_drawdown"] == "0.466630"
    assert b001["turnover"] == "270"
    assert b001["net_return"] == "2.073076"
    assert "validation period not inspected" in b001["notes"]


def test_phase1_ledger_records_b002_research_result_only():
    ledger_rows = rows()
    by_id = {row["experiment_id"]: row for row in ledger_rows}
    b002 = by_id["B002"]

    assert b002["cagr"] == "0.122232"
    assert b002["max_drawdown"] == "0.534276"
    assert b002["turnover"] == "199"
    assert b002["net_return"] == "1.241707"
    assert "Turnover gate FAIL" in b002["notes"]
    assert "drawdown gate FAIL" in b002["notes"]
    assert "validation period not inspected" in b002["notes"]


def test_phase1_ledger_records_b003_research_result_only():
    ledger_rows = rows()
    by_id = {row["experiment_id"]: row for row in ledger_rows}
    b003 = by_id["B003"]

    assert b003["cagr"] == "0.136461"
    assert b003["max_drawdown"] == "0.512654"
    assert b003["turnover"] == "124"
    assert b003["net_return"] == "1.448398"
    assert "Turnover gate PASS" in b003["notes"]
    assert "drawdown gate FAIL" in b003["notes"]
    assert "validation period not inspected" in b003["notes"]


def test_phase2_b004_rows_are_preregistered_and_blank():
    by_id = {row["experiment_id"]: row for row in rows()}
    b004 = by_id["B004"]
    robust = by_id["B004-S015"]

    assert b004["status"] == "PLANNED"
    assert b004["research_period"] == "2016-01-01..2022-12-31"
    assert b004["validation_period"] == "2023-01-01..2026-08-19"
    assert "SMA200" in b004["strategy"]
    assert "risk_on=TRI>SMA200" in b004["parameters"]
    assert "candidate 1 of maximum 3" in b004["notes"]

    assert robust["status"] == "PLANNED"
    assert robust["slippage_model"] == "adverse deterministic slippage 0.15% robustness"
    assert "Run only if B004 passes every baseline Phase 2 promotion gate" in robust["notes"]

    result_columns = (
        "cagr",
        "max_drawdown",
        "sharpe",
        "sortino",
        "calmar",
        "turnover",
        "net_return",
    )
    assert all(b004[column] == "" for column in result_columns)
    assert all(robust[column] == "" for column in result_columns)


def test_unrun_experiment_result_columns_remain_blank():
    result_columns = (
        "cagr",
        "max_drawdown",
        "sharpe",
        "sortino",
        "calmar",
        "turnover",
        "net_return",
    )

    for row in rows():
        if row["experiment_id"] in {"B001", "B002", "B003"}:
            continue
        assert all(row[column] == "" for column in result_columns)
