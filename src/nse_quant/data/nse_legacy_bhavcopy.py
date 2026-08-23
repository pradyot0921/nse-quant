"""Offline parser for legacy NSE CM bhavcopy files.

This module parses the pre-UDiFF `CM - Bhavcopy(csv)` ZIP format documented in
`docs/validation/LEGACY_CM_BHAVCOPY_FORMAT_SCAN_V0.md`. It intentionally does
not download files; saved raw CSV or single-CSV ZIP files must parse
deterministically without network access.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import csv
from pathlib import Path
import re
import zipfile
from typing import Iterable


EXPECTED_COLUMNS = (
    "SYMBOL",
    "SERIES",
    "OPEN",
    "HIGH",
    "LOW",
    "CLOSE",
    "LAST",
    "PREVCLOSE",
    "TOTTRDQTY",
    "TOTTRDVAL",
    "TIMESTAMP",
    "TOTALTRADES",
    "ISIN",
    "",
)

DEFAULT_SERIES = "EQ"
SOURCE_FORMAT = "NSE_CM_BHAVCOPY_CSV_ZIP"
VWAP_PRICE_TOLERANCE = Decimal("0.005")


class LegacyBhavcopyParseError(ValueError):
    """Raised when a legacy CM bhavcopy file cannot be parsed safely."""


class LegacyBhavcopySchemaError(LegacyBhavcopyParseError):
    """Raised when a legacy CM bhavcopy file has an unexpected schema."""


class LegacyBhavcopyDataQualityError(LegacyBhavcopyParseError):
    """Raised when row contents violate V0 data-quality rules."""


@dataclass(frozen=True)
class LegacyBhavcopyEquityBar:
    trade_date: date
    source_format: str
    symbol: str
    isin: str
    series: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    previous_close: Decimal
    last_price: Decimal
    volume: int
    traded_value: Decimal
    transaction_count: int


@dataclass(frozen=True)
class LegacyBhavcopyRejectedRow:
    row_number: int
    symbol: str
    series: str
    reason: str


@dataclass(frozen=True)
class LegacyBhavcopy:
    trade_date: date
    bars: tuple[LegacyBhavcopyEquityBar, ...]
    rejected_rows: tuple[LegacyBhavcopyRejectedRow, ...]
    rejected_series_counts: dict[str, int]
    source_name: str


def parse_cm_bhavcopy_file(
    path: str | Path,
    *,
    series: str = DEFAULT_SERIES,
) -> LegacyBhavcopy:
    """Parse a saved legacy NSE CM bhavcopy CSV or single-CSV ZIP file."""

    source = Path(path)
    rows, fieldnames = _read_rows(source)
    _validate_columns(fieldnames)
    if not rows:
        raise LegacyBhavcopyDataQualityError(f"{source.name}: file contains no rows")

    target_series = series.strip().upper()
    if not target_series:
        raise ValueError("series is required")

    dates = {_parse_legacy_date(row["TIMESTAMP"], field_name="TIMESTAMP") for row in rows}
    if len(dates) != 1:
        raise LegacyBhavcopyDataQualityError(
            f"{source.name}: multiple TIMESTAMP values: {sorted(dates)}"
        )

    trade_date = next(iter(dates))
    filename_date = date_from_cm_bhavcopy_filename(source.name)
    if filename_date is not None and filename_date != trade_date:
        raise LegacyBhavcopyDataQualityError(
            f"{source.name}: filename date {filename_date} does not match "
            f"TIMESTAMP {trade_date}"
        )

    rejected_series_counts = Counter(
        row["SERIES"].strip().upper()
        for row in rows
        if row["SERIES"].strip().upper() != target_series
    )

    bars = []
    rejected_rows = []
    seen_symbols: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        if row["SERIES"].strip().upper() != target_series:
            continue

        try:
            bar = _parse_eq_row(row, source_name=source.name, row_number=row_number)
            if bar.symbol in seen_symbols:
                raise LegacyBhavcopyDataQualityError(
                    f"duplicate {target_series} symbol {bar.symbol}"
                )
        except LegacyBhavcopyDataQualityError as exc:
            rejected_rows.append(
                LegacyBhavcopyRejectedRow(
                    row_number=row_number,
                    symbol=row.get("SYMBOL", "").strip().upper(),
                    series=row.get("SERIES", "").strip().upper(),
                    reason=str(exc),
                )
            )
            continue

        seen_symbols.add(bar.symbol)
        bars.append(bar)

    return LegacyBhavcopy(
        trade_date=trade_date,
        bars=tuple(bars),
        rejected_rows=tuple(rejected_rows),
        rejected_series_counts=dict(sorted(rejected_series_counts.items())),
        source_name=source.name,
    )


def date_from_cm_bhavcopy_filename(name: str) -> date | None:
    """Extract a session date from a legacy CM bhavcopy archive or CSV name."""

    match = re.fullmatch(
        r"cm(\d{2})([A-Z]{3})(\d{4})bhav\.csv(?:\.zip)?",
        name,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    day, month_name, year = match.groups()
    try:
        parsed = datetime.strptime(
            f"{day}{month_name.upper()}{year}", "%d%b%Y"
        ).date()
    except ValueError:
        raise LegacyBhavcopyDataQualityError(
            f"{name}: filename date is not valid"
        ) from None
    return parsed


def _read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if len(csv_names) != 1:
                raise LegacyBhavcopyParseError(
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
        raise LegacyBhavcopySchemaError(
            "unexpected legacy CM bhavcopy columns; "
            f"missing={missing or 'none'} extra={extra or 'none'}"
        )


def _parse_eq_row(
    row: dict[str, str],
    *,
    source_name: str,
    row_number: int,
) -> LegacyBhavcopyEquityBar:
    prefix = f"{source_name}:{row_number}"
    if row[""].strip():
        raise LegacyBhavcopyDataQualityError(
            f"{prefix}: trailing blank column must be empty"
        )

    symbol = _clean_required_text(row["SYMBOL"], field_name="SYMBOL", prefix=prefix)
    isin = _clean_required_text(row["ISIN"], field_name="ISIN", prefix=prefix)
    series = _clean_required_text(row["SERIES"], field_name="SERIES", prefix=prefix)

    open_price = _positive_decimal(row["OPEN"], field_name="OPEN", prefix=prefix)
    high_price = _positive_decimal(row["HIGH"], field_name="HIGH", prefix=prefix)
    low_price = _positive_decimal(row["LOW"], field_name="LOW", prefix=prefix)
    close_price = _positive_decimal(row["CLOSE"], field_name="CLOSE", prefix=prefix)
    last_price = _positive_decimal(row["LAST"], field_name="LAST", prefix=prefix)
    previous_close = _positive_decimal(
        row["PREVCLOSE"], field_name="PREVCLOSE", prefix=prefix
    )
    volume = _positive_int(row["TOTTRDQTY"], field_name="TOTTRDQTY", prefix=prefix)
    traded_value = _positive_decimal(row["TOTTRDVAL"], field_name="TOTTRDVAL", prefix=prefix)
    transaction_count = _positive_int(
        row["TOTALTRADES"], field_name="TOTALTRADES", prefix=prefix
    )

    if not (low_price <= open_price <= high_price):
        raise LegacyBhavcopyDataQualityError(f"{prefix}: OPEN outside low/high range")
    if not (low_price <= close_price <= high_price):
        raise LegacyBhavcopyDataQualityError(f"{prefix}: CLOSE outside low/high range")
    if not (low_price <= last_price <= high_price):
        raise LegacyBhavcopyDataQualityError(f"{prefix}: LAST outside low/high range")

    implied_vwap = traded_value / Decimal(volume)
    if not (
        low_price - VWAP_PRICE_TOLERANCE
        <= implied_vwap
        <= high_price + VWAP_PRICE_TOLERANCE
    ):
        raise LegacyBhavcopyDataQualityError(
            f"{prefix}: TOTTRDVAL/TOTTRDQTY {implied_vwap} outside low/high range"
        )

    return LegacyBhavcopyEquityBar(
        trade_date=_parse_legacy_date(row["TIMESTAMP"], field_name="TIMESTAMP"),
        source_format=SOURCE_FORMAT,
        symbol=symbol,
        isin=isin,
        series=series,
        open=open_price,
        high=high_price,
        low=low_price,
        close=close_price,
        previous_close=previous_close,
        last_price=last_price,
        volume=volume,
        traded_value=traded_value,
        transaction_count=transaction_count,
    )


def _clean_required_text(value: str, *, field_name: str, prefix: str) -> str:
    clean_value = value.strip().upper()
    if not clean_value:
        raise LegacyBhavcopyDataQualityError(f"{prefix}: {field_name} is required")
    return clean_value


def _positive_decimal(value: str, *, field_name: str, prefix: str) -> Decimal:
    try:
        amount = Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        raise LegacyBhavcopyDataQualityError(
            f"{prefix}: {field_name} is not a decimal"
        ) from None
    if amount <= 0:
        raise LegacyBhavcopyDataQualityError(f"{prefix}: {field_name} must be positive")
    return amount


def _positive_int(value: str, *, field_name: str, prefix: str) -> int:
    try:
        amount = int(value.strip())
    except (ValueError, AttributeError):
        raise LegacyBhavcopyDataQualityError(
            f"{prefix}: {field_name} is not an integer"
        ) from None
    if amount <= 0:
        raise LegacyBhavcopyDataQualityError(f"{prefix}: {field_name} must be positive")
    return amount


def _parse_legacy_date(value: str, *, field_name: str) -> date:
    try:
        return datetime.strptime(value.strip().upper(), "%d-%b-%Y").date()
    except ValueError:
        raise LegacyBhavcopyDataQualityError(
            f"{field_name} is not a DD-MMM-YYYY date: {value!r}"
        ) from None
