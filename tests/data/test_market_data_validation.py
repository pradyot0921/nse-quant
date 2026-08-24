from datetime import date
from decimal import Decimal
import csv
import zipfile

from nse_quant.data.market_data_bars import (
    SOURCE_CM_UDIFF,
    SOURCE_LEGACY_CM_BHAVCOPY,
)
from nse_quant.data.nse_acquisition import TradingSession
from nse_quant.data.nse_legacy_acquisition import cm_bhavcopy_raw_path
from nse_quant.data.nse_legacy_bhavcopy import EXPECTED_COLUMNS as LEGACY_COLUMNS
from nse_quant.data.nse_udiff import EXPECTED_COLUMNS as UDIFF_COLUMNS
from nse_quant.data.nse_acquisition import cm_udiff_raw_path
from nse_quant.data.validation import (
    validate_market_data_files,
    write_market_data_validation_report,
)


def session(session_date, session_type="NORMAL"):
    return TradingSession(session_date, session_type, "test calendar")


def legacy_row(**overrides):
    values = {
        "SYMBOL": "BEML",
        "SERIES": "EQ",
        "OPEN": "4453.70",
        "HIGH": "4505.00",
        "LOW": "4382.90",
        "CLOSE": "4399.80",
        "LAST": "4400.00",
        "PREVCLOSE": "4410.00",
        "TOTTRDQTY": "349959",
        "TOTTRDVAL": "1554003341.40",
        "TIMESTAMP": "05-Jul-24",
        "TOTALTRADES": "16988",
        "ISIN": "INE258A01016",
        "": "",
    }
    values.update(overrides)
    return values


def udiff_row(**overrides):
    values = {
        "TradDt": "2024-07-08",
        "BizDt": "2024-07-08",
        "Sgmt": "CM",
        "Src": "NSE",
        "FinInstrmTp": "STK",
        "FinInstrmId": "200",
        "ISIN": "INE258A01016",
        "TckrSymb": "BEML",
        "SctySrs": "EQ",
        "XpryDt": "",
        "FininstrmActlXpryDt": "",
        "StrkPric": "",
        "OptnTp": "",
        "FinInstrmNm": "BEML",
        "OpnPric": "4453.70",
        "HghPric": "4505.00",
        "LwPric": "4382.90",
        "ClsPric": "4399.80",
        "LastPric": "4400.00",
        "PrvsClsgPric": "4410.00",
        "UndrlygPric": "",
        "SttlmPric": "",
        "OpnIntrst": "",
        "ChngInOpnIntrst": "",
        "TtlTradgVol": "349959",
        "TtlTrfVal": "1554003341.40",
        "TtlNbOfTxsExctd": "16988",
        "SsnId": "F1",
        "NewBrdLotQty": "1",
        "Rmks": "",
        "Rsvd1": "",
        "Rsvd2": "",
        "Rsvd3": "",
        "Rsvd4": "",
    }
    values.update(overrides)
    return values


def write_zip(path, rows, *, columns, inner_name):
    path.parent.mkdir(parents=True, exist_ok=True)
    csv_path = path.with_suffix(".csv")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    with zipfile.ZipFile(path, "w") as archive:
        archive.write(csv_path, arcname=inner_name)
    csv_path.unlink()


def write_legacy_archive(raw_root, session_date, rows):
    path = cm_bhavcopy_raw_path(raw_root, session_date)
    write_zip(
        path,
        rows,
        columns=LEGACY_COLUMNS,
        inner_name=path.name.removesuffix(".zip"),
    )
    return path


def write_udiff_archive(raw_root, session_date, rows):
    path = cm_udiff_raw_path(raw_root, session_date)
    write_zip(
        path,
        rows,
        columns=UDIFF_COLUMNS,
        inner_name=path.name.removesuffix(".zip"),
    )
    return path


def test_validate_market_data_files_emits_canonical_bars_for_both_sources(tmp_path):
    write_legacy_archive(tmp_path, date(2024, 7, 5), [legacy_row()])
    write_udiff_archive(tmp_path, date(2024, 7, 8), [udiff_row()])

    report = validate_market_data_files(
        tmp_path,
        (session(date(2024, 7, 5)), session(date(2024, 7, 8))),
    )

    assert [record.status for record in report.records] == ["parsed", "parsed"]
    assert report.missing_files == ()
    assert report.file_failures == ()
    assert report.rejected_rows == ()
    assert [bar.source_format for bar in report.bars] == [
        SOURCE_LEGACY_CM_BHAVCOPY,
        SOURCE_CM_UDIFF,
    ]
    assert report.bars[0].close == Decimal("4399.80")


def test_validate_market_data_files_reports_missing_and_unexpected_files(tmp_path):
    write_udiff_archive(
        tmp_path,
        date(2024, 7, 9),
        [udiff_row(TradDt="2024-07-09", BizDt="2024-07-09")],
    )

    report = validate_market_data_files(tmp_path, (session(date(2024, 7, 8)),))

    assert [record.status for record in report.records] == ["missing_file"]
    assert len(report.missing_files) == 1
    assert report.missing_files[0].session_date == date(2024, 7, 8)
    assert report.unexpected_files == ()
    assert report.bars == ()


def test_validate_market_data_files_labels_unexpected_udiff_overlap_by_file_family(tmp_path):
    write_udiff_archive(
        tmp_path,
        date(2024, 7, 5),
        [udiff_row(TradDt="2024-07-05", BizDt="2024-07-05")],
    )

    report = validate_market_data_files(tmp_path, (session(date(2024, 7, 5)),))

    assert len(report.missing_files) == 1
    assert report.missing_files[0].source == "legacy_cm_bhavcopy"
    assert len(report.unexpected_files) == 1
    assert report.unexpected_files[0].session_date == date(2024, 7, 5)
    assert report.unexpected_files[0].source == "cm_udiff"


def test_validate_market_data_files_reports_file_level_parser_failure(tmp_path):
    path = cm_bhavcopy_raw_path(tmp_path, date(2024, 7, 5))
    path.parent.mkdir(parents=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(path.name.removesuffix(".zip"), "BAD\n1\n")

    report = validate_market_data_files(tmp_path, (session(date(2024, 7, 5)),))

    assert [record.status for record in report.records] == ["file_failed"]
    assert len(report.file_failures) == 1
    assert "unexpected legacy CM bhavcopy columns" in report.file_failures[0].reason
    assert report.bars == ()


def test_validate_market_data_files_keeps_good_rows_and_reports_rejected_rows(tmp_path):
    write_udiff_archive(
        tmp_path,
        date(2024, 7, 8),
        [
            udiff_row(),
            udiff_row(
                TckrSymb="ABC",
                ISIN="INE000A01010",
                PrvsClsgPric="0",
            ),
        ],
    )

    report = validate_market_data_files(tmp_path, (session(date(2024, 7, 8)),))

    assert [record.status for record in report.records] == ["parsed"]
    assert len(report.bars) == 1
    assert len(report.rejected_rows) == 1
    assert report.rejected_rows[0].symbol == "ABC"
    assert "PrvsClsgPric must be positive" in report.rejected_rows[0].reason


def test_validate_market_data_files_audits_special_but_excludes_from_research_bars(tmp_path):
    write_udiff_archive(tmp_path, date(2024, 7, 8), [udiff_row()])

    report = validate_market_data_files(
        tmp_path,
        (session(date(2024, 7, 8), "SPECIAL"),),
    )

    assert report.missing_files == ()
    assert report.records == ()
    assert report.bars == ()


def test_write_market_data_validation_report(tmp_path):
    write_udiff_archive(tmp_path, date(2024, 7, 8), [udiff_row()])
    report = validate_market_data_files(tmp_path, (session(date(2024, 7, 8)),))

    output = write_market_data_validation_report(
        report,
        tmp_path / "report.md",
        raw_root=tmp_path,
    )

    text = output.read_text(encoding="utf-8")
    assert "| Canonical bars emitted | 1 |" in text
    assert "## Missing Expected Raw Files" in text
    assert "None." in text
