from datetime import date
from decimal import Decimal
import csv
import zipfile

import pytest

from nse_quant.data.corporate_actions import CorporateActionType
from nse_quant.data.nse_acquisition import TradingSession
from nse_quant.data.nse_legacy_acquisition import cm_bhavcopy_raw_path
from nse_quant.data.nse_legacy_bhavcopy import EXPECTED_COLUMNS as LEGACY_COLUMNS
from nse_quant.data.processed_dataset import (
    ProcessedDatasetError,
    build_processed_dataset,
    load_universe_symbols,
    parse_corporate_action_rows,
    write_processed_dataset_report,
)


def session(session_date):
    return TradingSession(session_date, "NORMAL", "test")


def legacy_row(**overrides):
    values = {
        "SYMBOL": "ABC",
        "SERIES": "EQ",
        "OPEN": "100.00",
        "HIGH": "110.00",
        "LOW": "90.00",
        "CLOSE": "105.00",
        "LAST": "104.00",
        "PREVCLOSE": "99.00",
        "TOTTRDQTY": "1000",
        "TOTTRDVAL": "105000.00",
        "TIMESTAMP": "01-Jan-16",
        "TOTALTRADES": "10",
        "ISIN": "INE000A01010",
        "": "",
    }
    values.update(overrides)
    return values


def write_legacy_archive(raw_root, session_date, rows):
    path = cm_bhavcopy_raw_path(raw_root, session_date)
    path.parent.mkdir(parents=True, exist_ok=True)
    csv_path = path.with_suffix(".csv")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEGACY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    with zipfile.ZipFile(path, "w") as archive:
        archive.write(csv_path, arcname=path.name.removesuffix(".zip"))
    csv_path.unlink()


def ca_row(symbol="ABC", subject="Bonus 1:1", ex_date="04-Jan-2016"):
    return {
        "symbol": symbol,
        "series": "EQ",
        "subject": subject,
        "exDate": ex_date,
        "recDate": "-",
    }


def test_parse_corporate_action_rows_filters_to_selected_eq_symbols():
    actions = parse_corporate_action_rows(
        [
            ca_row("ABC", "Bonus 1:1"),
            ca_row("XYZ", "Bonus 1:1"),
            {**ca_row("ABC", "Bonus 1:1"), "series": "BE"},
        ],
        ["ABC"],
    )

    assert len(actions) == 1
    assert actions[0].symbol == "ABC"
    assert actions[0].action_type == CorporateActionType.BONUS


def test_build_processed_dataset_filters_universe_and_applies_adjustments(tmp_path):
    write_legacy_archive(
        tmp_path,
        date(2016, 1, 1),
        [
            legacy_row(),
            legacy_row(SYMBOL="XYZ", ISIN="INE000A01028"),
        ],
    )
    write_legacy_archive(
        tmp_path,
        date(2016, 1, 4),
        [
            legacy_row(
                OPEN="52.00",
                HIGH="55.00",
                LOW="50.00",
                CLOSE="53.00",
                LAST="53.00",
                PREVCLOSE="105.00",
                TOTTRDQTY="2000",
                TOTTRDVAL="106000.00",
                TIMESTAMP="04-Jan-16",
            ),
            legacy_row(SYMBOL="XYZ", ISIN="INE000A01028", TIMESTAMP="04-Jan-16"),
        ],
    )

    report = build_processed_dataset(
        raw_root=tmp_path,
        sessions=(session(date(2016, 1, 1)), session(date(2016, 1, 4))),
        universe_symbols=["ABC"],
        corporate_action_rows=[ca_row("ABC", "Bonus 1:1", "04-Jan-2016")],
        output_path=tmp_path / "processed.csv",
    )

    assert len(report.bars) == 2
    assert report.bars[0].symbol == "ABC"
    assert report.bars[0].adjusted_close == Decimal("52.500000")
    assert report.bars[0].adjusted_volume == Decimal("2000.000000")
    assert report.bars[1].adjusted_close == Decimal("53.000000")
    assert report.output_sha256
    text = (tmp_path / "processed.csv").read_text(encoding="utf-8")
    assert "XYZ" not in text
    assert "raw_traded_value" in text


def test_build_processed_dataset_refuses_missing_selected_symbol_bar(tmp_path):
    write_legacy_archive(tmp_path, date(2016, 1, 1), [legacy_row()])
    write_legacy_archive(
        tmp_path,
        date(2016, 1, 4),
        [legacy_row(SYMBOL="XYZ", ISIN="INE000A01028", TIMESTAMP="04-Jan-16")],
    )

    with pytest.raises(ProcessedDatasetError, match="missing symbol/session bars"):
        build_processed_dataset(
            raw_root=tmp_path,
            sessions=(session(date(2016, 1, 1)), session(date(2016, 1, 4))),
            universe_symbols=["ABC"],
            corporate_action_rows=[],
            output_path=tmp_path / "processed.csv",
        )


def test_build_processed_dataset_refuses_unsupported_selected_action(tmp_path):
    write_legacy_archive(tmp_path, date(2016, 1, 1), [legacy_row()])

    with pytest.raises(ProcessedDatasetError, match="unsupported corporate action"):
        build_processed_dataset(
            raw_root=tmp_path,
            sessions=(session(date(2016, 1, 1)),),
            universe_symbols=["ABC"],
            corporate_action_rows=[ca_row("ABC", "Rights 1:4", "01-Jan-2016")],
            output_path=tmp_path / "processed.csv",
        )


def test_load_universe_symbols_preserves_order(tmp_path):
    path = tmp_path / "universe.csv"
    path.write_text("symbol\nABC\nXYZ\n", encoding="utf-8")

    assert load_universe_symbols(path) == ("ABC", "XYZ")


def test_write_processed_dataset_report_records_hash_and_adjustments(tmp_path):
    write_legacy_archive(tmp_path, date(2016, 1, 1), [legacy_row()])
    write_legacy_archive(
        tmp_path,
        date(2016, 1, 4),
        [legacy_row(TIMESTAMP="04-Jan-16")],
    )
    report = build_processed_dataset(
        raw_root=tmp_path,
        sessions=(session(date(2016, 1, 1)), session(date(2016, 1, 4))),
        universe_symbols=["ABC"],
        corporate_action_rows=[ca_row("ABC", "Bonus 1:1", "04-Jan-2016")],
        output_path=tmp_path / "processed.csv",
    )

    output = write_processed_dataset_report(
        report,
        tmp_path / "report.md",
        project_root=tmp_path,
    )

    text = output.read_text(encoding="utf-8")
    assert "| Processed bars | 2 |" in text
    assert "Processed CSV SHA-256" in text
    assert "Bonus 1:1" in text
