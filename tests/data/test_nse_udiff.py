from datetime import date
from decimal import Decimal
import csv
import zipfile

import pytest

from nse_quant.data.nse_udiff import (
    EXPECTED_COLUMNS,
    UDiffDataQualityError,
    UDiffParseError,
    UDiffSchemaError,
    parse_cm_udiff_file,
)


def row(**overrides):
    values = {
        "TradDt": "2025-10-31",
        "BizDt": "2025-10-31",
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


def test_parse_cm_udiff_zip_normalizes_eq_rows_and_reports_rejected_series(tmp_path):
    source = tmp_path / "BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv.zip"
    write_zip(
        source,
        [
            row(),
            row(TckrSymb="XYZBE", SctySrs="BE", ISIN="INE000A01010"),
            row(TckrSymb="XYZSM", SctySrs="SM", ISIN="INE000A01011"),
        ],
    )

    bhavcopy = parse_cm_udiff_file(source)

    assert bhavcopy.trade_date == date(2025, 10, 31)
    assert bhavcopy.source_name == source.name
    assert bhavcopy.rejected_series_counts == {"BE": 1, "SM": 1}
    assert bhavcopy.session_ids == ("F1",)
    assert len(bhavcopy.bars) == 1

    bar = bhavcopy.bars[0]
    assert bar.symbol == "BEML"
    assert bar.isin == "INE258A01016"
    assert bar.series == "EQ"
    assert bar.open == Decimal("4453.70")
    assert bar.high == Decimal("4505.00")
    assert bar.low == Decimal("4382.90")
    assert bar.close == Decimal("4399.80")
    assert bar.volume == 349959
    assert bar.traded_value == Decimal("1554003341.40")
    assert bar.transaction_count == 16988


def test_parse_cm_udiff_csv_without_network(tmp_path):
    source = tmp_path / "BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv"
    write_csv(source, [row()])

    bhavcopy = parse_cm_udiff_file(source)

    assert bhavcopy.trade_date == date(2025, 10, 31)
    assert bhavcopy.bars[0].symbol == "BEML"


def test_parse_cm_udiff_rejects_unexpected_schema(tmp_path):
    source = tmp_path / "BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv"
    columns = [column for column in EXPECTED_COLUMNS if column != "TtlTrfVal"]
    write_csv(source, [row()], columns=columns)

    with pytest.raises(UDiffSchemaError, match="TtlTrfVal"):
        parse_cm_udiff_file(source)


def test_parse_cm_udiff_rejects_filename_date_mismatch(tmp_path):
    source = tmp_path / "BhavCopy_NSE_CM_0_0_0_20251103_F_0000.csv"
    write_csv(source, [row()])

    with pytest.raises(UDiffDataQualityError, match="filename date"):
        parse_cm_udiff_file(source)


def test_parse_cm_udiff_rejects_business_date_mismatch(tmp_path):
    source = tmp_path / "BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv"
    write_csv(source, [row(BizDt="2025-11-03")])

    with pytest.raises(UDiffDataQualityError, match="BizDt"):
        parse_cm_udiff_file(source)


def test_parse_cm_udiff_rejects_duplicate_eq_symbol(tmp_path):
    source = tmp_path / "BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv"
    write_csv(
        source,
        [
            row(),
            row(FinInstrmId="201", ISIN="INE258A01024"),
        ],
    )

    with pytest.raises(UDiffDataQualityError, match="duplicate EQ symbol BEML"):
        parse_cm_udiff_file(source)


@pytest.mark.parametrize(
    "overrides",
    [
        {"TtlTradgVol": "0"},
        {"TtlTrfVal": "0"},
        {"OpnPric": "0"},
        {"TtlNbOfTxsExctd": "0"},
    ],
)
def test_parse_cm_udiff_rejects_non_tradeable_eq_rows(tmp_path, overrides):
    source = tmp_path / "BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv"
    write_csv(source, [row(**overrides)])

    with pytest.raises(UDiffDataQualityError, match="must be positive"):
        parse_cm_udiff_file(source)


def test_parse_cm_udiff_rejects_vwap_outside_low_high_range(tmp_path):
    source = tmp_path / "BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv"
    write_csv(source, [row(TtlTrfVal="100000000.00")])

    with pytest.raises(UDiffDataQualityError, match="outside low/high"):
        parse_cm_udiff_file(source)


def test_parse_cm_udiff_rejects_price_outside_low_high_range(tmp_path):
    source = tmp_path / "BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv"
    write_csv(source, [row(OpnPric="5000.00")])

    with pytest.raises(UDiffDataQualityError, match="OpnPric"):
        parse_cm_udiff_file(source)


def test_parse_cm_udiff_requires_single_csv_inside_zip(tmp_path):
    source = tmp_path / "BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("one.csv", "")
        archive.writestr("two.csv", "")

    with pytest.raises(UDiffParseError, match="exactly one CSV"):
        parse_cm_udiff_file(source)
