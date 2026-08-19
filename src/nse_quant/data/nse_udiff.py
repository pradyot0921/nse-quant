"""Offline parser for NSE CM-UDiFF bhavcopy files.

This module intentionally does not download files. A saved raw CM-UDiFF CSV or
CSV ZIP must parse deterministically without network access.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
import csv
from pathlib import Path
import re
import zipfile
from typing import Iterable


EXPECTED_COLUMNS = (
    "TradDt",
    "BizDt",
    "Sgmt",
    "Src",
    "FinInstrmTp",
    "FinInstrmId",
    "ISIN",
    "TckrSymb",
    "SctySrs",
    "XpryDt",
    "FininstrmActlXpryDt",
    "StrkPric",
    "OptnTp",
    "FinInstrmNm",
    "OpnPric",
    "HghPric",
    "LwPric",
    "ClsPric",
    "LastPric",
    "PrvsClsgPric",
    "UndrlygPric",
    "SttlmPric",
    "OpnIntrst",
    "ChngInOpnIntrst",
    "TtlTradgVol",
    "TtlTrfVal",
    "TtlNbOfTxsExctd",
    "SsnId",
    "NewBrdLotQty",
    "Rmks",
    "Rsvd1",
    "Rsvd2",
    "Rsvd3",
    "Rsvd4",
)

DEFAULT_SERIES = "EQ"


class UDiffParseError(ValueError):
    """Raised when a CM-UDiFF file cannot be parsed safely."""


class UDiffSchemaError(UDiffParseError):
    """Raised when a CM-UDiFF file has an unexpected schema."""


class UDiffDataQualityError(UDiffParseError):
    """Raised when row contents violate V0 data-quality rules."""


@dataclass(frozen=True)
class UDiffEquityBar:
    trade_date: date
    business_date: date
    symbol: str
    isin: str
    series: str
    instrument_type: str
    instrument_id: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    previous_close: Decimal
    last_price: Decimal
    volume: int
    traded_value: Decimal
    transaction_count: int
    session_id: str


@dataclass(frozen=True)
class UDiffBhavcopy:
    trade_date: date
    bars: tuple[UDiffEquityBar, ...]
    rejected_series_counts: dict[str, int]
    session_ids: tuple[str, ...]
    source_name: str


def parse_cm_udiff_file(path: str | Path, *, series: str = DEFAULT_SERIES) -> UDiffBhavcopy:
    """Parse a saved NSE CM-UDiFF CSV or single-CSV ZIP file."""

    source = Path(path)
    rows, fieldnames = _read_rows(source)
    _validate_columns(fieldnames)
    if not rows:
        raise UDiffDataQualityError(f"{source.name}: file contains no rows")

    target_series = series.strip().upper()
    if not target_series:
        raise ValueError("series is required")

    dates = {_parse_date(row["TradDt"], field_name="TradDt") for row in rows}
    business_dates = {_parse_date(row["BizDt"], field_name="BizDt") for row in rows}
    if len(dates) != 1:
        raise UDiffDataQualityError(f"{source.name}: multiple TradDt values: {sorted(dates)}")
    if len(business_dates) != 1:
        raise UDiffDataQualityError(
            f"{source.name}: multiple BizDt values: {sorted(business_dates)}"
        )

    trade_date = next(iter(dates))
    filename_date = _date_from_filename(source.name)
    if filename_date is not None and filename_date != trade_date:
        raise UDiffDataQualityError(
            f"{source.name}: filename date {filename_date} does not match TradDt {trade_date}"
        )

    rejected_series_counts = Counter(
        row["SctySrs"].strip().upper()
        for row in rows
        if row["SctySrs"].strip().upper() != target_series
    )
    session_ids = tuple(sorted({row["SsnId"].strip().upper() for row in rows}))

    bars = []
    seen_symbols: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        if row["SctySrs"].strip().upper() != target_series:
            continue

        bar = _parse_eq_row(row, source_name=source.name, row_number=row_number)
        if bar.symbol in seen_symbols:
            raise UDiffDataQualityError(
                f"{source.name}:{row_number}: duplicate {target_series} symbol {bar.symbol}"
            )
        seen_symbols.add(bar.symbol)
        bars.append(bar)

    return UDiffBhavcopy(
        trade_date=trade_date,
        bars=tuple(bars),
        rejected_series_counts=dict(sorted(rejected_series_counts.items())),
        session_ids=session_ids,
        source_name=source.name,
    )


def _read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if len(csv_names) != 1:
                raise UDiffParseError(
                    f"{path.name}: expected exactly one CSV in ZIP, found {len(csv_names)}"
                )
            with archive.open(csv_names[0]) as raw:
                text_rows = (line.decode("utf-8-sig") for line in raw)
                return _read_csv_rows(text_rows)

    with path.open(encoding="utf-8-sig", newline="") as handle:
        return _read_csv_rows(handle)


def _read_csv_rows(lines: Iterable[str]) -> tuple[list[dict[str, str]], list[str]]:
    reader = csv.DictReader(lines)
    fieldnames = list(reader.fieldnames or [])
    return list(reader), fieldnames


def _validate_columns(fieldnames: list[str]) -> None:
    if tuple(fieldnames) != EXPECTED_COLUMNS:
        missing = sorted(set(EXPECTED_COLUMNS) - set(fieldnames))
        extra = sorted(set(fieldnames) - set(EXPECTED_COLUMNS))
        raise UDiffSchemaError(
            "unexpected CM-UDiFF columns; "
            f"missing={missing or 'none'} extra={extra or 'none'}"
        )


def _parse_eq_row(
    row: dict[str, str],
    *,
    source_name: str,
    row_number: int,
) -> UDiffEquityBar:
    prefix = f"{source_name}:{row_number}"
    symbol = _clean_required_text(row["TckrSymb"], field_name="TckrSymb", prefix=prefix)
    isin = _clean_required_text(row["ISIN"], field_name="ISIN", prefix=prefix)
    series = _clean_required_text(row["SctySrs"], field_name="SctySrs", prefix=prefix)
    instrument_type = _clean_required_text(
        row["FinInstrmTp"], field_name="FinInstrmTp", prefix=prefix
    )
    instrument_id = _clean_required_text(
        row["FinInstrmId"], field_name="FinInstrmId", prefix=prefix
    )
    session_id = _clean_required_text(row["SsnId"], field_name="SsnId", prefix=prefix)

    open_price = _positive_decimal(row["OpnPric"], field_name="OpnPric", prefix=prefix)
    high_price = _positive_decimal(row["HghPric"], field_name="HghPric", prefix=prefix)
    low_price = _positive_decimal(row["LwPric"], field_name="LwPric", prefix=prefix)
    close_price = _positive_decimal(row["ClsPric"], field_name="ClsPric", prefix=prefix)
    last_price = _positive_decimal(row["LastPric"], field_name="LastPric", prefix=prefix)
    previous_close = _positive_decimal(
        row["PrvsClsgPric"], field_name="PrvsClsgPric", prefix=prefix
    )
    volume = _positive_int(row["TtlTradgVol"], field_name="TtlTradgVol", prefix=prefix)
    traded_value = _positive_decimal(row["TtlTrfVal"], field_name="TtlTrfVal", prefix=prefix)
    transaction_count = _positive_int(
        row["TtlNbOfTxsExctd"], field_name="TtlNbOfTxsExctd", prefix=prefix
    )

    if not (low_price <= open_price <= high_price):
        raise UDiffDataQualityError(f"{prefix}: OpnPric outside low/high range")
    if not (low_price <= close_price <= high_price):
        raise UDiffDataQualityError(f"{prefix}: ClsPric outside low/high range")
    if not (low_price <= last_price <= high_price):
        raise UDiffDataQualityError(f"{prefix}: LastPric outside low/high range")

    implied_vwap = traded_value / Decimal(volume)
    if not (low_price <= implied_vwap <= high_price):
        raise UDiffDataQualityError(
            f"{prefix}: TtlTrfVal/TtlTradgVol {implied_vwap} outside low/high range"
        )

    return UDiffEquityBar(
        trade_date=_parse_date(row["TradDt"], field_name="TradDt"),
        business_date=_parse_date(row["BizDt"], field_name="BizDt"),
        symbol=symbol,
        isin=isin,
        series=series,
        instrument_type=instrument_type,
        instrument_id=instrument_id,
        open=open_price,
        high=high_price,
        low=low_price,
        close=close_price,
        previous_close=previous_close,
        last_price=last_price,
        volume=volume,
        traded_value=traded_value,
        transaction_count=transaction_count,
        session_id=session_id,
    )


def _clean_required_text(value: str, *, field_name: str, prefix: str) -> str:
    clean_value = value.strip().upper()
    if not clean_value:
        raise UDiffDataQualityError(f"{prefix}: {field_name} is required")
    return clean_value


def _positive_decimal(value: str, *, field_name: str, prefix: str) -> Decimal:
    try:
        amount = Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        raise UDiffDataQualityError(f"{prefix}: {field_name} is not a decimal") from None
    if amount <= 0:
        raise UDiffDataQualityError(f"{prefix}: {field_name} must be positive")
    return amount


def _positive_int(value: str, *, field_name: str, prefix: str) -> int:
    try:
        amount = int(value.strip())
    except (ValueError, AttributeError):
        raise UDiffDataQualityError(f"{prefix}: {field_name} is not an integer") from None
    if amount <= 0:
        raise UDiffDataQualityError(f"{prefix}: {field_name} must be positive")
    return amount


def _parse_date(value: str, *, field_name: str) -> date:
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        raise UDiffDataQualityError(f"{field_name} is not an ISO date: {value!r}") from None


def _date_from_filename(name: str) -> date | None:
    match = re.search(r"_(\d{8})_", name)
    if match is None:
        return None
    raw = match.group(1)
    return date(int(raw[:4]), int(raw[4:6]), int(raw[6:]))
