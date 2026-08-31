import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "experiments" / "ledger.csv"


def rows():
    with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        return tuple(csv.DictReader(handle))


def test_phase1_ledger_references_frozen_universe_and_dataset_versions():
    expected_ids = {
        "B001",
        "B001-S015",
        "B002",
        "B002-S015",
        "B003",
        "B003-S015",
    }
    ledger_rows = rows()

    assert {row["experiment_id"] for row in ledger_rows} == expected_ids
    for row in ledger_rows:
        assert row["status"] == "PLANNED"
        assert row["universe_version"] == "nifty100_v0_20_d037"
        assert row["data_version"] == "nifty100_v0_adjusted_ohlcv_d039"
        assert "pending" not in row["universe_version"].lower()
        assert "pending" not in row["data_version"].lower()


def test_phase1_ledger_result_columns_remain_blank_before_strategy_runs():
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
        assert all(row[column] == "" for column in result_columns)
