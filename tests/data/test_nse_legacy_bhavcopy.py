from datetime import date
from decimal import Decimal
import csv
import zipfile

import pytest

from nse_quant.data.nse_legacy_bhavcopy import (
    EXPECTED_COLUMNS,
    SOURCE_FORMAT,
    LegacyBhavcopyDataQualityError,
    LegacyBhavcopyParseError,
    LegacyBhavcopySchemaError,
    date_from_cm_bhavcopy_filename,
    parse_cm_bhavcopy_file,
)


def row(**overrides):
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
        "TIMESTAMP": "31-OCT-2025",
        "TOTALTRADES": "16988",
        "ISIN": "INE258A01016",
        "": "",
    }
    values.update(overrides)
    return values


def write_csv(path, rows, *, columns=EXPECTED_COLUMNS):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_zip(path, rows, *, inner_name=None, columns=EXPECTED_COLUMNS):
    csv_path = path.with_suffix(".csv")
    write_csv(csv_path, rows, columns=columns)
    with zipfile.ZipFile(path, "w") as archive:
        archive.write(csv_path, arcname=inner_name or csv_path.name)
    csv_path.unlink()


def test_parse_legacy_bhavcopy_zip_normalizes_eq_rows_and_reports_rejected_series(tmp_path):
    source = tmp_path / "cm31OCT2025bhav.csv.zip"
    write_zip(
        source,
        [
            row(),
            row(SYMBOL="XYZBE", SERIES="BE", ISIN="INE000A01010"),
            row(SYMBOL="XYZSM", SERIES="SM", ISIN="INE000A01011"),
        ],
    )

    bhavcopy = parse_cm_bhavcopy_file(source)

    assert bhavcopy.trade_date == date(2025, 10, 31)
    assert bhavcopy.source_name == source.name
    assert bhavcopy.rejected_series_counts == {"BE": 1, "SM": 1}
    assert bhavcopy.rejected_rows == ()
    assert len(bhavcopy.bars) == 1

    bar = bhavcopy.bars[0]
    assert bar.trade_date == date(2025, 10, 31)
    assert bar.source_format == SOURCE_FORMAT
    assert bar.symbol == "BEML"
    assert bar.isin == "INE258A01016"
    assert bar.series == "EQ"
    assert bar.open == Decimal("4453.70")
    assert bar.high == Decimal("4505.00")
    assert bar.low == Decimal("4382.90")
    assert bar.close == Decimal("4399.80")
    assert bar.previous_close == Decimal("4410.00")
    assert bar.last_price == Decimal("4400.00")
    assert bar.volume == 349959
    assert bar.traded_value == Decimal("1554003341.40")
    assert bar.transaction_count == 16988


def test_parse_legacy_bhavcopy_csv_without_network(tmp_path):
    source = tmp_path / "cm31OCT2025bhav.csv"
    write_csv(source, [row()])

    bhavcopy = parse_cm_bhavcopy_file(source)

    assert bhavcopy.trade_date == date(2025, 10, 31)
    assert bhavcopy.bars[0].symbol == "BEML"

def test_parse_legacy_bhavcopy_accepts_two_digit_year_timestamp(tmp_path):
    source = tmp_path / "cm13JUL2020bhav.csv"
    write_csv(source, [row(TIMESTAMP="13-Jul-20")])

    bhavcopy = parse_cm_bhavcopy_file(source)

    assert bhavcopy.trade_date == date(2020, 7, 13)
    assert bhavcopy.bars[0].trade_date == date(2020, 7, 13)

def test_legacy_filename_date_parser_accepts_archive_and_csv_names():
    assert date_from_cm_bhavcopy_filename("cm04JAN2016bhav.csv.zip") == date(
        2016, 1, 4
    )
    assert date_from_cm_bhavcopy_filename("cm05JUL2024bhav.csv") == date(2024, 7, 5)
    assert date_from_cm_bhavcopy_filename("other.zip") is None


def test_parse_legacy_bhavcopy_rejects_unexpected_schema(tmp_path):
    source = tmp_path / "cm31OCT2025bhav.csv"
    columns = [column for column in EXPECTED_COLUMNS if column != "TOTTRDVAL"]
    write_csv(source, [row()], columns=columns)

    with pytest.raises(LegacyBhavcopySchemaError, match="TOTTRDVAL"):
        parse_cm_bhavcopy_file(source)


def test_parse_legacy_bhavcopy_rejects_filename_date_mismatch(tmp_path):
    source = tmp_path / "cm03NOV2025bhav.csv"
    write_csv(source, [row()])

    with pytest.raises(LegacyBhavcopyDataQualityError, match="filename date"):
        parse_cm_bhavcopy_file(source)


def test_parse_legacy_bhavcopy_rejects_multiple_timestamp_values(tmp_path):
    source = tmp_path / "legacy.csv"
    write_csv(source, [row(), row(SYMBOL="ABC", TIMESTAMP="03-NOV-2025")])

    with pytest.raises(LegacyBhavcopyDataQualityError, match="multiple TIMESTAMP"):
        parse_cm_bhavcopy_file(source)


def test_parse_legacy_bhavcopy_rejects_duplicate_eq_symbol_as_row_failure(tmp_path):
    source = tmp_path / "cm31OCT2025bhav.csv"
    write_csv(
        source,
        [
            row(),
            row(ISIN="INE258A01024"),
        ],
    )

    bhavcopy = parse_cm_bhavcopy_file(source)

    assert len(bhavcopy.bars) == 1
    assert len(bhavcopy.rejected_rows) == 1
    assert bhavcopy.rejected_rows[0].symbol == "BEML"
    assert "duplicate EQ symbol BEML" in bhavcopy.rejected_rows[0].reason


def test_parse_legacy_bhavcopy_keeps_good_rows_when_one_eq_row_is_rejected(tmp_path):
    source = tmp_path / "cm31OCT2025bhav.csv"
    write_csv(
        source,
        [
            row(),
            row(SYMBOL="BADROW", ISIN="INE000A01010", PREVCLOSE="0"),
            row(SYMBOL="GOODROW", ISIN="INE000A01011"),
        ],
    )

    bhavcopy = parse_cm_bhavcopy_file(source)

    assert [bar.symbol for bar in bhavcopy.bars] == ["BEML", "GOODROW"]
    assert len(bhavcopy.rejected_rows) == 1
    assert bhavcopy.rejected_rows[0].row_number == 3
    assert bhavcopy.rejected_rows[0].symbol == "BADROW"
    assert "PREVCLOSE must be positive" in bhavcopy.rejected_rows[0].reason


@pytest.mark.parametrize(
    "overrides",
    [
        {"TOTTRDQTY": "0"},
        {"TOTTRDVAL": "0"},
        {"OPEN": "0"},
        {"TOTALTRADES": "0"},
        {"ISIN": ""},
        {"": "unexpected"},
    ],
)
def test_parse_legacy_bhavcopy_rejects_invalid_eq_rows(tmp_path, overrides):
    source = tmp_path / "cm31OCT2025bhav.csv"
    write_csv(source, [row(**overrides)])

    bhavcopy = parse_cm_bhavcopy_file(source)

    assert bhavcopy.bars == ()
    assert len(bhavcopy.rejected_rows) == 1


def test_parse_legacy_bhavcopy_rejects_vwap_outside_low_high_range(tmp_path):
    source = tmp_path / "cm31OCT2025bhav.csv"
    write_csv(source, [row(TOTTRDVAL="100000000.00")])

    bhavcopy = parse_cm_bhavcopy_file(source)

    assert bhavcopy.bars == ()
    assert len(bhavcopy.rejected_rows) == 1
    assert "outside low/high" in bhavcopy.rejected_rows[0].reason


def test_parse_legacy_bhavcopy_allows_half_paisa_vwap_range_tolerance(tmp_path):
    source = tmp_path / "cm31OCT2025bhav.csv"
    tolerated_traded_value = (Decimal("4505.001") * Decimal("349959")).quantize(
        Decimal("0.01")
    )
    write_csv(source, [row(TOTTRDVAL=str(tolerated_traded_value))])

    bhavcopy = parse_cm_bhavcopy_file(source)

    assert len(bhavcopy.bars) == 1
    assert bhavcopy.rejected_rows == ()


def test_parse_legacy_bhavcopy_rejects_price_outside_low_high_range(tmp_path):
    source = tmp_path / "cm31OCT2025bhav.csv"
    write_csv(source, [row(OPEN="5000.00")])

    bhavcopy = parse_cm_bhavcopy_file(source)

    assert bhavcopy.bars == ()
    assert len(bhavcopy.rejected_rows) == 1
    assert "OPEN" in bhavcopy.rejected_rows[0].reason


def test_parse_legacy_bhavcopy_requires_single_csv_inside_zip(tmp_path):
    source = tmp_path / "cm31OCT2025bhav.csv.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("one.csv", "")
        archive.writestr("two.csv", "")

    with pytest.raises(LegacyBhavcopyParseError, match="exactly one CSV"):
        parse_cm_bhavcopy_file(source)
