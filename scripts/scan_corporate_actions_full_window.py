from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from http.client import HTTPException
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener
import argparse
import json
import time

from nse_quant.data.corporate_actions import (
    CorporateActionRecord,
    CorporateActionType,
    ParsedCorporateAction,
    parse_corporate_action,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "docs"
    / "validation"
    / "CORPORATE_ACTION_FULL_WINDOW_SCAN_V0.md"
)
DEFAULT_RAW_OUTPUT = PROJECT_ROOT / "work" / "corporate_actions_full_window_rows.json"
NSE_BASE = "https://www.nseindia.com"
NSE_CA_PAGE = f"{NSE_BASE}/companies-listing/corporate-filings-actions"
NSE_CA_API = f"{NSE_BASE}/api/corporates-corporateActions"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class RowFailure:
    chunk_start: date
    chunk_end: date
    symbol: str
    series: str
    reason: str
    row: dict[str, object]


@dataclass(frozen=True)
class ScanResult:
    rows: tuple[dict[str, object], ...]
    eq_rows: tuple[dict[str, object], ...]
    parsed_actions: tuple[ParsedCorporateAction, ...]
    row_failures: tuple[RowFailure, ...]
    chunks: tuple[tuple[date, date, int], ...]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2016-01-01")
    parser.add_argument("--end", default="2026-08-19")
    parser.add_argument("--chunk", choices=("month", "quarter", "year"), default="year")
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--raw-output", default=str(DEFAULT_RAW_OUTPUT))
    parser.add_argument("--fail-on-row-failures", action="store_true")
    args = parser.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    result = scan_corporate_actions(
        start,
        end,
        chunk=args.chunk,
        delay_seconds=args.delay_seconds,
        max_retries=args.max_retries,
    )

    raw_output = Path(args.raw_output)
    raw_output.parent.mkdir(parents=True, exist_ok=True)
    raw_output.write_text(
        json.dumps(list(result.rows), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    output = write_report(result, args.output, start=start, end=end, chunk=args.chunk)

    print(f"Wrote {output}")
    print(f"Wrote raw rows {raw_output}")
    print(f"endpoint_rows={len(result.rows)}")
    print(f"eq_rows={len(result.eq_rows)}")
    print(f"parsed_actions={len(result.parsed_actions)}")
    print(f"row_failures={len(result.row_failures)}")
    print_category_counts(result.parsed_actions)

    if args.fail_on_row_failures and result.row_failures:
        return 1
    return 0


def scan_corporate_actions(
    start: date,
    end: date,
    *,
    chunk: str,
    delay_seconds: float,
    max_retries: int,
) -> ScanResult:
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    _prime_session(opener)

    rows: list[dict[str, object]] = []
    eq_rows: list[dict[str, object]] = []
    parsed_actions: list[ParsedCorporateAction] = []
    row_failures: list[RowFailure] = []
    chunks: list[tuple[date, date, int]] = []

    ranges = tuple(_date_chunks(start, end, chunk=chunk))
    for index, (chunk_start, chunk_end) in enumerate(ranges, start=1):
        print(f"{index}/{len(ranges)} fetching {chunk_start} to {chunk_end}", flush=True)
        chunk_rows = _fetch_actions(
            opener,
            chunk_start,
            chunk_end,
            max_retries=max_retries,
            retry_delay_seconds=delay_seconds,
        )
        rows.extend(chunk_rows)
        chunks.append((chunk_start, chunk_end, len(chunk_rows)))

        for row in chunk_rows:
            series = str(row.get("series", "")).strip().upper()
            if series != "EQ":
                continue
            eq_rows.append(row)
            try:
                record = _record_from_row(row)
            except ValueError as exc:
                row_failures.append(
                    RowFailure(
                        chunk_start=chunk_start,
                        chunk_end=chunk_end,
                        symbol=str(row.get("symbol", "")).strip().upper(),
                        series=series,
                        reason=str(exc),
                        row=row,
                    )
                )
                continue
            parsed_actions.append(parse_corporate_action(record))

        print(
            f"{index}/{len(ranges)} done {chunk_start} to {chunk_end}; "
            f"rows={len(rows)} eq={len(eq_rows)} parsed={len(parsed_actions)} "
            f"row_failures={len(row_failures)}",
            flush=True,
        )
        time.sleep(delay_seconds)

    return ScanResult(
        rows=tuple(rows),
        eq_rows=tuple(eq_rows),
        parsed_actions=tuple(parsed_actions),
        row_failures=tuple(row_failures),
        chunks=tuple(chunks),
    )


def write_report(
    result: ScanResult,
    output_path: str | Path,
    *,
    start: date,
    end: date,
    chunk: str,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    category_counts = Counter(action.action_type for action in result.parsed_actions)
    unsupported = [
        action
        for action in result.parsed_actions
        if action.action_type == CorporateActionType.UNSUPPORTED
    ]
    supported = [
        action
        for action in result.parsed_actions
        if action.action_type in {CorporateActionType.SPLIT, CorporateActionType.BONUS}
    ]
    series_counts = Counter(str(row.get("series", "")).strip().upper() for row in result.rows)

    lines = [
        "# NSE Corporate-Action Full-Window Scan V0",
        "",
        f"Source: NSE corporate actions endpoint, `index=equities`",
        f"Window: `{start}` to `{end}`",
        f"Chunking: `{chunk}`",
        f"Endpoint rows: `{len(result.rows)}`",
        f"EQ rows scanned: `{len(result.eq_rows)}`",
        "",
        "This scan validates the conservative corporate-action parser against the",
        "full pre-registered research and validation window before universe",
        "selection.",
        "",
        "## Category Frequency",
        "",
        "| Category | Count |",
        "| --- | ---: |",
    ]
    for category in CorporateActionType:
        lines.append(f"| {category.name} | {category_counts[category]} |")

    lines.extend(
        [
            "",
            "## Chunk Row Counts",
            "",
            "| From | To | Endpoint Rows |",
            "| --- | --- | ---: |",
        ]
    )
    for chunk_start, chunk_end, count in result.chunks:
        lines.append(f"| {chunk_start} | {chunk_end} | {count} |")

    lines.extend(
        [
            "",
            "## Endpoint Series Counts",
            "",
            "| Series | Rows |",
            "| --- | ---: |",
        ]
    )
    for series, count in sorted(series_counts.items()):
        lines.append(f"| {series or '(blank)'} | {count} |")

    lines.extend(
        [
            "",
            "## Unsupported Purposes",
            "",
            "These records intentionally remain quarantined in V0. A universe candidate",
            "with one of these unsupported actions inside the frozen window must be",
            "excluded unless a later decision adds deterministic support before",
            "universe selection.",
            "",
            "| Count | Symbols | Purpose | First Example |",
            "| ---: | ---: | --- | --- |",
        ]
    )
    unsupported_groups: dict[str, list[ParsedCorporateAction]] = defaultdict(list)
    for action in unsupported:
        unsupported_groups[action.purpose].append(action)
    for purpose, actions in sorted(
        unsupported_groups.items(),
        key=lambda item: (-len(item[1]), item[0].lower()),
    ):
        symbols = {action.symbol for action in actions}
        first = min(actions, key=lambda action: (action.ex_date, action.symbol))
        lines.append(
            f"| {len(actions)} | {len(symbols)} | {_md(purpose)} | "
            f"{first.symbol} {first.ex_date} |"
        )

    lines.extend(
        [
            "",
            "## Parsed Split And Bonus Purposes",
            "",
            "| Category | Count | Purpose | Price Factor | Volume Factor | First Example |",
            "| --- | ---: | --- | ---: | ---: | --- |",
        ]
    )
    supported_groups: dict[
        tuple[CorporateActionType, str, Decimal, Decimal],
        list[ParsedCorporateAction],
    ] = defaultdict(list)
    for action in supported:
        supported_groups[
            (
                action.action_type,
                action.purpose,
                action.price_adjustment_factor,
                action.volume_adjustment_factor,
            )
        ].append(action)
    for key, actions in sorted(
        supported_groups.items(),
        key=lambda item: (item[0][0].value, item[0][1].lower()),
    ):
        action_type, purpose, price_factor, volume_factor = key
        first = min(actions, key=lambda action: (action.ex_date, action.symbol))
        lines.append(
            f"| {action_type.name} | {len(actions)} | {_md(purpose)} | "
            f"{price_factor} | {volume_factor} | {first.symbol} {first.ex_date} |"
        )

    lines.extend(
        [
            "",
            "## Row-Level Failures",
            "",
        ]
    )
    if result.row_failures:
        lines.extend(
            [
                "| Chunk | Symbol | Series | Reason |",
                "| --- | --- | --- | --- |",
            ]
        )
        for failure in result.row_failures:
            lines.append(
                f"| {failure.chunk_start} to {failure.chunk_end} | "
                f"{_md(failure.symbol)} | {_md(failure.series)} | "
                f"{_md(failure.reason)} |"
            )
    else:
        lines.append("None.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This report is a corpus scan, not a universe freeze. It identifies the",
            "full-window corporate-action vocabulary that the V0 parser can and cannot",
            "classify deterministically. Universe selection must still apply D-021 to",
            "candidate symbols over this same window.",
            "",
        ]
    )

    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def print_category_counts(actions: Iterable[ParsedCorporateAction]) -> None:
    counts = Counter(action.action_type for action in actions)
    for category in CorporateActionType:
        print(f"{category.value}={counts[category]}")


def _record_from_row(row: dict[str, object]) -> CorporateActionRecord:
    symbol = str(row.get("symbol", "")).strip().upper()
    purpose = str(row.get("subject", "")).strip()
    ex_date = _parse_nse_date(str(row.get("exDate", "")).strip(), field_name="exDate")
    raw_record_date = str(row.get("recDate", "")).strip()
    record_date = (
        None
        if raw_record_date in {"", "-"}
        else _parse_nse_date(raw_record_date, field_name="recDate")
    )
    return CorporateActionRecord(
        symbol=symbol,
        purpose=purpose,
        ex_date=ex_date,
        record_date=record_date,
    )


def _parse_nse_date(value: str, *, field_name: str) -> date:
    try:
        return datetime.strptime(value, "%d-%b-%Y").date()
    except ValueError:
        raise ValueError(f"{field_name} is not DD-MMM-YYYY: {value!r}") from None


def _fetch_actions(
    opener,
    start: date,
    end: date,
    *,
    max_retries: int,
    retry_delay_seconds: float,
) -> list[dict[str, object]]:
    params = urlencode(
        {
            "index": "equities",
            "from_date": _nse_param_date(start),
            "to_date": _nse_param_date(end),
        }
    )
    url = f"{NSE_CA_API}?{params}"
    attempts = max_retries + 1
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers=_headers())
            with opener.open(request, timeout=120) as response:
                body = response.read()
            payload = json.loads(body.decode("utf-8"))
            if not isinstance(payload, list):
                raise RuntimeError(f"unexpected NSE corporate-actions payload: {type(payload)!r}")
            return payload
        except (TimeoutError, HTTPException, URLError, HTTPError, json.JSONDecodeError) as exc:
            if attempt == attempts:
                raise RuntimeError(f"failed fetching {url}: {exc}") from exc
            time.sleep(retry_delay_seconds)

    raise AssertionError("unreachable retry loop exit")


def _prime_session(opener) -> None:
    request = Request(NSE_CA_PAGE, headers=_headers())
    with opener.open(request, timeout=60) as response:
        response.read(1024)


def _headers() -> dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Accept": "application/json,text/plain,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": NSE_CA_PAGE,
    }


def _date_chunks(start: date, end: date, *, chunk: str) -> Iterable[tuple[date, date]]:
    current = start
    while current <= end:
        if chunk == "month":
            next_start = _add_months(current, 1)
        elif chunk == "quarter":
            next_start = _add_months(current, 3)
        elif chunk == "year":
            next_start = date(current.year + 1, 1, 1)
        else:
            raise ValueError(f"unsupported chunk {chunk!r}")
        chunk_end = min(end, next_start - timedelta(days=1))
        yield current, chunk_end
        current = chunk_end + timedelta(days=1)


def _add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def _nse_param_date(value: date) -> str:
    return f"{value:%d-%m-%Y}"


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
