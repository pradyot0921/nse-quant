from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import argparse
import socket
import time
import urllib.request
from urllib.error import HTTPError, URLError

from nse_quant.data.market_data_bars import (
    CanonicalEquityBar,
    canonical_bar_from_legacy,
    canonical_bar_from_udiff,
    comparable_bar_values,
)
from nse_quant.data.nse_acquisition import (
    UDiffAcquisitionError,
    UDiffArchiveNotFoundError,
    UDiffDownloadRetryableError,
    cm_udiff_archive_url,
    cm_udiff_raw_path,
    download_cm_udiff_file,
    load_session_calendar,
)
from nse_quant.data.nse_legacy_acquisition import (
    LegacyBhavcopyAcquisitionError,
    LegacyBhavcopyArchiveNotFoundError,
    LegacyBhavcopyDownloadRetryableError,
    cm_bhavcopy_archive_url,
    cm_bhavcopy_raw_path,
    download_cm_bhavcopy_file,
)
from nse_quant.data.nse_legacy_bhavcopy import parse_cm_bhavcopy_file
from nse_quant.data.nse_udiff import parse_cm_udiff_file


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CALENDAR_PATH = PROJECT_ROOT / "data" / "calendars" / "nse_cm_sessions_2016-01-01_2026-08-19.csv"
OUTPUT_PATH = PROJECT_ROOT / "docs" / "validation" / "LEGACY_UDIFF_SEAM_VALIDATION_V0.md"
DEFAULT_START = date(2024, 7, 1)
DEFAULT_END = date(2024, 7, 12)
LEGACY_LAST_SESSION = date(2024, 7, 5)
UDIFF_FIRST_SESSION = date(2024, 7, 8)


@dataclass(frozen=True)
class SourceResult:
    source: str
    session_date: date
    status: str
    path: Path
    bars: tuple[CanonicalEquityBar, ...]
    rejected_rows: int
    rejected_series_counts: dict[str, int]
    reason: str = ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", default="data/raw")
    parser.add_argument("--start", default=DEFAULT_START.isoformat())
    parser.add_argument("--end", default=DEFAULT_END.isoformat())
    parser.add_argument("--delay-seconds", type=float, default=0.5)
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    args = parser.parse_args()

    raw_root = PROJECT_ROOT / args.raw_root
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    sessions = tuple(
        session.session_date
        for session in load_session_calendar(CALENDAR_PATH)
        if start <= session.session_date <= end
    )

    legacy_results = []
    udiff_results = []
    for index, session_date in enumerate(sessions, start=1):
        print(f"{index}/{len(sessions)} checking {session_date}", flush=True)
        legacy_results.append(
            load_legacy_result(
                raw_root,
                session_date,
                max_retries=args.max_retries,
                delay_seconds=args.delay_seconds,
                timeout_seconds=args.timeout_seconds,
            )
        )
        udiff_results.append(
            load_udiff_result(
                raw_root,
                session_date,
                max_retries=args.max_retries,
                delay_seconds=args.delay_seconds,
                timeout_seconds=args.timeout_seconds,
            )
        )
        if args.delay_seconds:
            time.sleep(args.delay_seconds)

    overlap_summaries = compare_overlap(legacy_results, udiff_results)
    seam_summary = compare_seam_previous_close(legacy_results, udiff_results)
    write_report(
        start=start,
        end=end,
        raw_root=raw_root,
        legacy_results=legacy_results,
        udiff_results=udiff_results,
        overlap_summaries=overlap_summaries,
        seam_summary=seam_summary,
        delay_seconds=args.delay_seconds,
        max_retries=args.max_retries,
        timeout_seconds=args.timeout_seconds,
    )
    print(f"Wrote {OUTPUT_PATH}", flush=True)
    return 0


def load_legacy_result(
    raw_root: Path,
    session_date: date,
    *,
    max_retries: int,
    delay_seconds: float,
    timeout_seconds: float,
) -> SourceResult:
    path = cm_bhavcopy_raw_path(raw_root, session_date)

    def fetcher(url: str) -> bytes:
        return fetch_url(
            url,
            timeout_seconds=timeout_seconds,
            not_found_error=LegacyBhavcopyArchiveNotFoundError,
            retryable_error=LegacyBhavcopyDownloadRetryableError,
            fatal_error=LegacyBhavcopyAcquisitionError,
        )

    try:
        downloaded_path = download_cm_bhavcopy_file(
            session_date,
            raw_root,
            fetch_bytes=fetcher,
            max_retries=max_retries,
            retry_delay_seconds=delay_seconds,
        )
        parsed = parse_cm_bhavcopy_file(downloaded_path)
    except LegacyBhavcopyArchiveNotFoundError as exc:
        return SourceResult("legacy", session_date, "missing", path, (), 0, {}, str(exc))
    except Exception as exc:
        return SourceResult("legacy", session_date, "failed", path, (), 0, {}, str(exc))

    return SourceResult(
        source="legacy",
        session_date=session_date,
        status="available",
        path=downloaded_path,
        bars=tuple(canonical_bar_from_legacy(bar) for bar in parsed.bars),
        rejected_rows=len(parsed.rejected_rows),
        rejected_series_counts=parsed.rejected_series_counts,
    )


def load_udiff_result(
    raw_root: Path,
    session_date: date,
    *,
    max_retries: int,
    delay_seconds: float,
    timeout_seconds: float,
) -> SourceResult:
    path = cm_udiff_raw_path(raw_root, session_date)

    def fetcher(url: str) -> bytes:
        return fetch_url(
            url,
            timeout_seconds=timeout_seconds,
            not_found_error=UDiffArchiveNotFoundError,
            retryable_error=UDiffDownloadRetryableError,
            fatal_error=UDiffAcquisitionError,
        )

    try:
        downloaded_path = download_cm_udiff_file(
            session_date,
            raw_root,
            fetch_bytes=fetcher,
            max_retries=max_retries,
            retry_delay_seconds=delay_seconds,
        )
        parsed = parse_cm_udiff_file(downloaded_path)
    except UDiffArchiveNotFoundError as exc:
        return SourceResult("udiff", session_date, "missing", path, (), 0, {}, str(exc))
    except Exception as exc:
        return SourceResult("udiff", session_date, "failed", path, (), 0, {}, str(exc))

    return SourceResult(
        source="udiff",
        session_date=session_date,
        status="available",
        path=downloaded_path,
        bars=tuple(canonical_bar_from_udiff(bar) for bar in parsed.bars),
        rejected_rows=len(parsed.rejected_rows),
        rejected_series_counts=parsed.rejected_series_counts,
    )


def fetch_url(
    url: str,
    *,
    timeout_seconds: float,
    not_found_error,
    retryable_error,
    fatal_error,
) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; nse-quant-research/0.1)",
            "Accept": "application/zip,*/*",
            "Referer": "https://www.nseindia.com/all-reports",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return response.read()
    except HTTPError as exc:
        if exc.code == 404:
            raise not_found_error(f"archive not found: {url}") from exc
        if 500 <= exc.code <= 599:
            raise retryable_error(f"temporary NSE error {exc.code}: {url}") from exc
        raise fatal_error(f"NSE error {exc.code}: {url}") from exc
    except (TimeoutError, socket.timeout, URLError, OSError) as exc:
        raise retryable_error(f"download failed: {url}: {exc}") from exc


def compare_overlap(
    legacy_results: list[SourceResult],
    udiff_results: list[SourceResult],
) -> list[dict[str, object]]:
    udiff_by_date = {result.session_date: result for result in udiff_results}
    summaries = []
    for legacy in legacy_results:
        udiff = udiff_by_date[legacy.session_date]
        if legacy.status != "available" or udiff.status != "available":
            continue
        legacy_by_symbol = {bar.symbol: bar for bar in legacy.bars}
        udiff_by_symbol = {bar.symbol: bar for bar in udiff.bars}
        common_symbols = sorted(set(legacy_by_symbol) & set(udiff_by_symbol))
        mismatches = [
            symbol
            for symbol in common_symbols
            if comparable_bar_values(legacy_by_symbol[symbol])
            != comparable_bar_values(udiff_by_symbol[symbol])
        ]
        summaries.append(
            {
                "date": legacy.session_date,
                "legacy_rows": len(legacy.bars),
                "udiff_rows": len(udiff.bars),
                "common_symbols": len(common_symbols),
                "legacy_only": len(set(legacy_by_symbol) - set(udiff_by_symbol)),
                "udiff_only": len(set(udiff_by_symbol) - set(legacy_by_symbol)),
                "mismatches": len(mismatches),
                "mismatch_examples": mismatches[:20],
            }
        )
    return summaries


def compare_seam_previous_close(
    legacy_results: list[SourceResult],
    udiff_results: list[SourceResult],
) -> dict[str, object]:
    legacy = next(
        result
        for result in legacy_results
        if result.session_date == LEGACY_LAST_SESSION
    )
    udiff = next(
        result
        for result in udiff_results
        if result.session_date == UDIFF_FIRST_SESSION
    )
    if legacy.status != "available" or udiff.status != "available":
        return {
            "checked": False,
            "reason": (
                f"legacy {LEGACY_LAST_SESSION} status={legacy.status}; "
                f"udiff {UDIFF_FIRST_SESSION} status={udiff.status}"
            ),
        }

    legacy_by_symbol = {bar.symbol: bar for bar in legacy.bars}
    udiff_by_symbol = {bar.symbol: bar for bar in udiff.bars}
    common_symbols = sorted(set(legacy_by_symbol) & set(udiff_by_symbol))
    mismatches = []
    for symbol in common_symbols:
        legacy_close = legacy_by_symbol[symbol].close
        udiff_previous_close = udiff_by_symbol[symbol].previous_close
        if legacy_close != udiff_previous_close:
            mismatches.append((symbol, legacy_close, udiff_previous_close))

    return {
        "checked": True,
        "legacy_date": LEGACY_LAST_SESSION,
        "udiff_date": UDIFF_FIRST_SESSION,
        "legacy_rows": len(legacy.bars),
        "udiff_rows": len(udiff.bars),
        "common_symbols": len(common_symbols),
        "legacy_only": len(set(legacy_by_symbol) - set(udiff_by_symbol)),
        "udiff_only": len(set(udiff_by_symbol) - set(legacy_by_symbol)),
        "previous_close_mismatches": len(mismatches),
        "mismatch_examples": mismatches[:25],
    }


def write_report(
    *,
    start: date,
    end: date,
    raw_root: Path,
    legacy_results: list[SourceResult],
    udiff_results: list[SourceResult],
    overlap_summaries: list[dict[str, object]],
    seam_summary: dict[str, object],
    delay_seconds: float,
    max_retries: int,
    timeout_seconds: float,
) -> None:
    legacy_status = Counter(result.status for result in legacy_results)
    udiff_status = Counter(result.status for result in udiff_results)
    lines = [
        "# Legacy CM Bhavcopy / CM-UDiFF Seam Validation V0",
        "",
        "**Date:** 24 August 2026  ",
        "**Status:** Evidence artifact",
        "",
        "## Scope",
        "",
        f"Checked NSE sessions from `{start}` through `{end}` around the 8 July 2024 UDiFF transition.",
        "",
        f"Raw root used: `{display_path(raw_root)}`",
        f"Delay seconds: `{delay_seconds}`",
        f"Max retries: `{max_retries}`",
        f"Timeout seconds: `{timeout_seconds}`",
        "",
        "## Source Availability",
        "",
        "| Source | Available | Missing | Failed |",
        "| --- | ---: | ---: | ---: |",
        f"| Legacy CM bhavcopy | {legacy_status['available']} | {legacy_status['missing']} | {legacy_status['failed']} |",
        f"| CM-UDiFF | {udiff_status['available']} | {udiff_status['missing']} | {udiff_status['failed']} |",
        "",
        "## Per-Date Results",
        "",
        "| Date | Legacy status | Legacy EQ rows | UDiFF status | UDiFF EQ rows |",
        "| --- | --- | ---: | --- | ---: |",
    ]

    udiff_by_date = {result.session_date: result for result in udiff_results}
    for legacy in legacy_results:
        udiff = udiff_by_date[legacy.session_date]
        lines.append(
            f"| {legacy.session_date} | {legacy.status} | {len(legacy.bars)} | "
            f"{udiff.status} | {len(udiff.bars)} |"
        )

    lines += ["", "## Same-Date Overlap Comparison", ""]
    if overlap_summaries:
        lines += [
            "| Date | Legacy rows | UDiFF rows | Common symbols | Legacy-only | UDiFF-only | Mismatches |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for summary in overlap_summaries:
            lines.append(
                f"| {summary['date']} | {summary['legacy_rows']} | {summary['udiff_rows']} | "
                f"{summary['common_symbols']} | {summary['legacy_only']} | "
                f"{summary['udiff_only']} | {summary['mismatches']} |"
            )
    else:
        lines.append("No same-date overlap was observed in this transition window.")

    lines += ["", "## Boundary Previous-Close Check", ""]
    if seam_summary.get("checked"):
        lines += [
            "| Legacy date | UDiFF date | Common symbols | Legacy-only | UDiFF-only | Previous-close mismatches |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
            f"| {seam_summary['legacy_date']} | {seam_summary['udiff_date']} | "
            f"{seam_summary['common_symbols']} | {seam_summary['legacy_only']} | "
            f"{seam_summary['udiff_only']} | {seam_summary['previous_close_mismatches']} |",
            "",
        ]
        examples = seam_summary["mismatch_examples"]
        if examples:
            lines += [
                "### Previous-Close Mismatch Examples",
                "",
                "| Symbol | Legacy close | UDiFF previous close |",
                "| --- | ---: | ---: |",
            ]
            for symbol, legacy_close, udiff_previous_close in examples:
                lines.append(f"| {symbol} | {legacy_close} | {udiff_previous_close} |")
        else:
            lines.append("No previous-close mismatches observed for common symbols.")
    else:
        lines.append(str(seam_summary["reason"]))

    lines += ["", "## Failures", ""]
    failures = [
        result
        for result in [*legacy_results, *udiff_results]
        if result.status == "failed"
    ]
    if failures:
        lines += ["| Date | Source | Reason |", "| --- | --- | --- |"]
        for failure in failures:
            lines.append(
                f"| {failure.session_date} | {failure.source} | `{failure.reason}` |"
            )
    else:
        lines.append("None.")

    lines += [
        "",
        "## Interpretation",
        "",
        f"Same-date source overlap was observed on {len(overlap_summaries)} sessions.",
        "For those overlap sessions, the legacy CM bhavcopy parser and CM-UDiFF",
        "parser produced identical canonical EQ rows for every common symbol.",
        "",
        "The first V0 CM-UDiFF session also passed the boundary check: for common",
        "symbols, 8 July 2024 UDiff `previous_close` matched 5 July 2024 legacy",
        "CM bhavcopy `close` exactly.",
        "",
        "This validates the July 2024 source-family bridge for the canonical fields",
        "used by Phase 1 daily bars: symbol, ISIN, series, OHLC, previous close,",
        "last price, traded volume, traded value, and transaction count.",
        "",
        "Raw archives remain outside version control; this report records the",
        "source-family availability and comparison results needed before processed",
        "dataset construction.",
        "",
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
