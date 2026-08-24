"""Nifty 100 TRI benchmark acquisition and validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Callable, Iterable
from urllib.request import Request, urlopen
import csv
import json

from nse_quant.data.nse_acquisition import TradingSession, research_sessions


NIFTY100_TRI_NAME = "NIFTY 100"
NIFTY_INDICES_HISTORICAL_DATA_URL = "https://www.niftyindices.com/reports/historical-data"
NIFTY_INDICES_TRI_ENDPOINT = (
    "https://www.niftyindices.com/BackPage/getTotalReturnIndexString"
)
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)


class BenchmarkDataError(RuntimeError):
    """Raised when benchmark data cannot be used safely."""


class BenchmarkAcquisitionError(BenchmarkDataError):
    """Raised when the official benchmark endpoint cannot be fetched."""


@dataclass(frozen=True)
class TriBenchmarkBar:
    index_name: str
    trade_date: date
    total_return_index: Decimal
    net_total_return_index: Decimal | None


@dataclass(frozen=True)
class BenchmarkValidationReport:
    index_name: str
    bars: tuple[TriBenchmarkBar, ...]
    sessions_checked: tuple[TradingSession, ...]
    missing_dates: tuple[date, ...]
    extra_dates: tuple[date, ...]

    @property
    def has_blocking_problems(self) -> bool:
        return bool(self.missing_dates)


def fetch_nifty_tri_response(
    *,
    index_name: str,
    start_date: date,
    end_date: date,
    fetch_bytes: Callable[[str, bytes, dict[str, str]], bytes] | None = None,
) -> bytes:
    """Fetch one official NSE Indices TRI response body."""

    payload = {
        "cinfo": (
            "{"
            f"'name':'{index_name}',"
            f"'startDate':'{_request_date(start_date)}',"
            f"'endDate':'{_request_date(end_date)}',"
            f"'indexName':'{index_name}'"
            "}"
        )
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json,text/javascript,*/*;q=0.01",
        "Referer": NIFTY_INDICES_HISTORICAL_DATA_URL,
        "Origin": "https://www.niftyindices.com",
        "User-Agent": DEFAULT_USER_AGENT,
    }
    fetcher = fetch_bytes or _fetch_url
    return fetcher(NIFTY_INDICES_TRI_ENDPOINT, body, headers)


def parse_nifty_tri_response(
    content: bytes | str,
    *,
    expected_index_name: str = NIFTY100_TRI_NAME,
) -> tuple[TriBenchmarkBar, ...]:
    """Parse NSE Indices' Total Returns Index response."""

    text = content.decode("utf-8-sig") if isinstance(content, bytes) else content
    try:
        outer = json.loads(text)
    except json.JSONDecodeError as exc:
        raise BenchmarkDataError("NSE Indices TRI response is not JSON") from exc

    if isinstance(outer, list):
        rows = outer
    elif isinstance(outer, dict) and "d" in outer:
        try:
            rows = json.loads(outer["d"])
        except (TypeError, json.JSONDecodeError) as exc:
            raise BenchmarkDataError("NSE Indices TRI payload field 'd' is not JSON") from exc
    else:
        raise BenchmarkDataError("NSE Indices TRI response is neither a row list nor field 'd'")
    if not isinstance(rows, list):
        raise BenchmarkDataError("NSE Indices TRI payload must be a list")
    if not rows:
        raise BenchmarkDataError("NSE Indices TRI payload is empty")

    bars = tuple(_bar_from_row(row, expected_index_name=expected_index_name) for row in rows)
    _validate_unique_dates(bars)
    return tuple(sorted(bars, key=lambda bar: bar.trade_date))


def validate_benchmark_sessions(
    bars: Iterable[TriBenchmarkBar],
    sessions: Iterable[TradingSession],
    *,
    include_special: bool = False,
) -> BenchmarkValidationReport:
    """Validate that benchmark rows cover every expected research-bar session."""

    bar_tuple = tuple(sorted(bars, key=lambda bar: bar.trade_date))
    if not bar_tuple:
        raise BenchmarkDataError("benchmark bars are empty")
    index_names = {bar.index_name.upper() for bar in bar_tuple}
    if len(index_names) != 1:
        raise BenchmarkDataError(f"multiple benchmark index names: {sorted(index_names)}")

    session_tuple = research_sessions(sessions, include_special=include_special)
    expected_dates = {session.session_date for session in session_tuple}
    observed_dates = {bar.trade_date for bar in bar_tuple}

    return BenchmarkValidationReport(
        index_name=bar_tuple[0].index_name,
        bars=bar_tuple,
        sessions_checked=session_tuple,
        missing_dates=tuple(sorted(expected_dates - observed_dates)),
        extra_dates=tuple(sorted(observed_dates - expected_dates)),
    )


def write_tri_benchmark_csv(
    bars: Iterable[TriBenchmarkBar],
    output_path: str | Path,
) -> Path:
    """Write benchmark bars to a deterministic CSV."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "trade_date",
                "index_name",
                "total_return_index",
                "net_total_return_index",
            ]
        )
        for bar in sorted(bars, key=lambda item: item.trade_date):
            writer.writerow(
                [
                    bar.trade_date.isoformat(),
                    bar.index_name,
                    str(bar.total_return_index),
                    "" if bar.net_total_return_index is None else str(bar.net_total_return_index),
                ]
            )
    return output


def write_benchmark_validation_report(
    report: BenchmarkValidationReport,
    output_path: str | Path,
    *,
    source_url: str = NIFTY_INDICES_HISTORICAL_DATA_URL,
) -> Path:
    """Write a Markdown benchmark validation artifact."""

    output = Path(output_path)
    lines = [
        "# Nifty 100 TRI Benchmark Data V0",
        "",
        "**Status:** Evidence artifact",
        "",
        "## Source",
        "",
        f"Official source: `{source_url}`",
        "Report: `Total returns Index Values`",
        f"Index: `{report.index_name}`",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Benchmark rows | {len(report.bars)} |",
        f"| Sessions checked | {len(report.sessions_checked)} |",
        f"| Missing benchmark dates | {len(report.missing_dates)} |",
        f"| Extra benchmark dates | {len(report.extra_dates)} |",
        "",
        "## Date Range",
        "",
        f"First benchmark row: `{report.bars[0].trade_date}`",
        f"Last benchmark row: `{report.bars[-1].trade_date}`",
        "",
    ]
    _append_dates(lines, "Missing Benchmark Dates", report.missing_dates)
    _append_dates(lines, "Extra Benchmark Dates", report.extra_dates)
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The official TRI series is the benchmark for Phase 1. Missing benchmark",
            "dates are blocking because strategy NAV and benchmark drawdown must be",
            "computed over the identical evaluation period.",
            "",
            "Extra benchmark dates are reported for audit. They are not blocking",
            "by themselves when they correspond to special sessions excluded from",
            "default V0 research bars under D-029.",
            "",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def _fetch_url(url: str, body: bytes, headers: dict[str, str]) -> bytes:
    request = Request(url, data=body, headers=headers)
    try:
        with urlopen(request, timeout=60) as response:
            return response.read()
    except OSError as exc:
        raise BenchmarkAcquisitionError(f"failed to fetch benchmark data: {exc}") from exc


def _bar_from_row(
    row: object,
    *,
    expected_index_name: str,
) -> TriBenchmarkBar:
    if not isinstance(row, dict):
        raise BenchmarkDataError("NSE Indices TRI row is not an object")
    index_name = str(row.get("Index Name", "")).strip()
    if index_name.upper() != expected_index_name.upper():
        raise BenchmarkDataError(
            f"unexpected TRI index name {index_name!r}; expected {expected_index_name!r}"
        )
    total_return_index = _positive_decimal(row.get("TotalReturnsIndex"), "TotalReturnsIndex")
    raw_ntr = str(row.get("NTR_Value", "")).strip()
    return TriBenchmarkBar(
        index_name=expected_index_name,
        trade_date=_response_date(str(row.get("Date", "")).strip()),
        total_return_index=total_return_index,
        net_total_return_index=(
            None if raw_ntr in {"", "-"} else _positive_decimal(raw_ntr, "NTR_Value")
        ),
    )


def _validate_unique_dates(bars: tuple[TriBenchmarkBar, ...]) -> None:
    seen = set()
    duplicates = []
    for bar in bars:
        if bar.trade_date in seen:
            duplicates.append(bar.trade_date)
        seen.add(bar.trade_date)
    if duplicates:
        raise BenchmarkDataError(f"duplicate benchmark dates: {duplicates}")


def _positive_decimal(value: object, field_name: str) -> Decimal:
    amount = Decimal(str(value).strip())
    if amount <= 0:
        raise BenchmarkDataError(f"{field_name} must be positive")
    return amount


def _request_date(value: date) -> str:
    return f"{value:%d-%b-%Y}"


def _response_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%d %b %Y").date()
    except ValueError:
        raise BenchmarkDataError(f"Date is not DD MMM YYYY: {value!r}") from None


def _append_dates(lines: list[str], title: str, dates: tuple[date, ...]) -> None:
    lines.extend(["", f"## {title}", ""])
    if not dates:
        lines.append("None.")
        return
    lines.extend(["| Date |", "| --- |"])
    for value in dates[:100]:
        lines.append(f"| {value} |")
    if len(dates) > 100:
        lines.append(f"| ... {len(dates) - 100} more |")
