from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
import argparse
import socket
import time
import urllib.request
from urllib.error import HTTPError, URLError

from nse_quant.data.nse_acquisition import load_session_calendar
from nse_quant.data.nse_legacy_acquisition import (
    LegacyBhavcopyAcquisitionError,
    LegacyBhavcopyArchiveNotFoundError,
    LegacyBhavcopyDownloadRetryableError,
    cm_bhavcopy_raw_path,
    cm_bhavcopy_archive_url,
    download_cm_bhavcopy_file,
)
from nse_quant.data.nse_legacy_bhavcopy import (
    LegacyBhavcopyParseError,
    parse_cm_bhavcopy_file,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CALENDAR_PATH = PROJECT_ROOT / "data" / "calendars" / "nse_cm_sessions_2016-01-01_2026-08-19.csv"
LEGACY_END = date(2024, 7, 5)
OUTPUT_PATH = PROJECT_ROOT / "docs" / "validation" / "LEGACY_CM_BHAVCOPY_FULL_WINDOW_SCAN_V0.md"


def fetch_fast(url: str, *, timeout_seconds: float = 20.0) -> bytes:
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
            raise LegacyBhavcopyArchiveNotFoundError(f"archive not found: {url}") from exc
        if 500 <= exc.code <= 599:
            raise LegacyBhavcopyDownloadRetryableError(f"temporary NSE error {exc.code}: {url}") from exc
        raise LegacyBhavcopyAcquisitionError(f"NSE error {exc.code}: {url}") from exc
    except (TimeoutError, socket.timeout, URLError, OSError) as exc:
        raise LegacyBhavcopyDownloadRetryableError(f"download failed: {url}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", default="data/raw")
    parser.add_argument("--delay-seconds", type=float, default=0.5)
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    raw_root = PROJECT_ROOT / args.raw_root
    sessions = [
        session
        for session in load_session_calendar(CALENDAR_PATH)
        if session.session_date <= LEGACY_END
    ]
    if args.limit is not None:
        sessions = sessions[: args.limit]

    totals = Counter()
    status_counts = Counter()
    series_counts = Counter()
    rejected_reasons = Counter()
    rejected_examples = []
    missing_archives = []
    failed_archives = []
    file_failures = []

    def fetcher(url: str) -> bytes:
        return fetch_fast(url, timeout_seconds=args.timeout_seconds)

    for index, session in enumerate(sessions, start=1):
        session_date = session.session_date
        path_before = cm_bhavcopy_raw_path(raw_root, session_date)
        existed_before = path_before.exists()

        print(
            f"{index}/{len(sessions)} starting {session_date} "
            f"{'reuse' if existed_before else 'download'} "
            f"{cm_bhavcopy_archive_url(session_date)}",
            flush=True,
        )

        try:
            path = download_cm_bhavcopy_file(
                session_date,
                raw_root,
                fetch_bytes=fetcher,
                max_retries=args.max_retries,
                retry_delay_seconds=args.delay_seconds,
            )
            status_counts["reused" if existed_before else "downloaded"] += 1
        except LegacyBhavcopyArchiveNotFoundError as exc:
            missing_archives.append((session_date, str(exc)))
            print(f"{index}/{len(sessions)} missing {session_date}", flush=True)
            continue
        except (LegacyBhavcopyAcquisitionError, TimeoutError, OSError, socket.timeout) as exc:
            failed_archives.append((session_date, repr(exc)))
            print(f"{index}/{len(sessions)} failed {session_date}: {exc!r}", flush=True)
            continue

        try:
            parsed = parse_cm_bhavcopy_file(path)
        except LegacyBhavcopyParseError as exc:
            file_failures.append((session_date, path.name, str(exc)))
            print(f"{index}/{len(sessions)} parse-failed {session_date}: {exc}", flush=True)
            continue

        totals["files_parsed"] += 1
        totals["eq_rows"] += len(parsed.bars)
        totals["rejected_rows"] += len(parsed.rejected_rows)
        totals["total_rows_seen"] += (
            len(parsed.bars)
            + len(parsed.rejected_rows)
            + sum(parsed.rejected_series_counts.values())
        )

        for series, count in parsed.rejected_series_counts.items():
            series_counts[series] += count

        for rejected in parsed.rejected_rows:
            category = classify_rejection(rejected.reason)
            rejected_reasons[category] += 1
            if len(rejected_examples) < 100:
                rejected_examples.append(
                    (session_date, rejected.row_number, rejected.symbol, rejected.series, rejected.reason)
                )

        print(
            f"{index}/{len(sessions)} done {session_date}; "
            f"parsed={totals['files_parsed']} "
            f"missing={len(missing_archives)} "
            f"failed={len(failed_archives)} "
            f"file_failures={len(file_failures)} "
            f"row_rejections={totals['rejected_rows']}",
            flush=True,
        )

        if args.delay_seconds:
            time.sleep(args.delay_seconds)

    write_report(
        sessions=sessions,
        status_counts=status_counts,
        totals=totals,
        series_counts=series_counts,
        missing_archives=missing_archives,
        failed_archives=failed_archives,
        file_failures=file_failures,
        rejected_reasons=rejected_reasons,
        rejected_examples=rejected_examples,
        raw_root=raw_root,
        limit=args.limit,
        delay_seconds=args.delay_seconds,
        max_retries=args.max_retries,
        timeout_seconds=args.timeout_seconds,
    )
    print(f"Wrote {OUTPUT_PATH}", flush=True)
    return 0


def classify_rejection(reason: str) -> str:
    text = reason.lower()
    if "isin is required" in text:
        return "blank ISIN"
    if "duplicate eq symbol" in text:
        return "duplicate EQ symbol"
    if "must be positive" in text and any(x in text for x in ["open", "high", "low", "close", "last", "prevclose"]):
        return "zero/blank OHLC"
    if "tottrdqty must be positive" in text:
        return "zero/blank volume"
    if "tottrdval must be positive" in text:
        return "zero/blank traded value"
    if "outside low/high" in text:
        return "VWAP or price low/high breach"
    return "other row rejection"


def write_report(
    *,
    sessions,
    status_counts,
    totals,
    series_counts,
    missing_archives,
    failed_archives,
    file_failures,
    rejected_reasons,
    rejected_examples,
    raw_root,
    limit,
    delay_seconds,
    max_retries,
    timeout_seconds,
) -> None:
    special_count = sum(1 for session in sessions if session.session_type == "SPECIAL")
    normal_count = len(sessions) - special_count

    lines = [
        "# Legacy CM Bhavcopy Full-Window Scan V0",
        "",
        "**Date:** 24 August 2026  ",
        "**Status:** Evidence artifact",
        "",
        "## Scope",
        "",
        "Legacy NSE `CM - Bhavcopy(csv)` files scanned for:",
        "",
        "```text",
        "2016-01-01 through 2024-07-05, inclusive",
        "```",
        "",
        f"Raw root used: `{raw_root}`",
        f"Delay seconds: `{delay_seconds}`",
        f"Max retries: `{max_retries}`",
        f"Timeout seconds: `{timeout_seconds}`",
        "",
    ]

    if limit is not None:
        lines += ["**Warning:** This run used `--limit`; it is not the final full-window scan.", ""]

    lines += [
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Expected legacy sessions | {len(sessions)} |",
        f"| Normal sessions | {normal_count} |",
        f"| Special sessions | {special_count} |",
        f"| Downloaded archives | {status_counts['downloaded']} |",
        f"| Reused archives | {status_counts['reused']} |",
        f"| Parsed files | {totals['files_parsed']} |",
        f"| Missing archives | {len(missing_archives)} |",
        f"| Failed archive downloads/reuse | {len(failed_archives)} |",
        f"| File-level parser failures | {len(file_failures)} |",
        f"| Total parsed rows counted | {totals['total_rows_seen']} |",
        f"| Parsed EQ rows | {totals['eq_rows']} |",
        f"| Rejected EQ rows | {totals['rejected_rows']} |",
        "",
        "## Non-EQ Series Counts",
        "",
    ]

    if series_counts:
        lines += ["| Series | Rows |", "| --- | ---: |"]
        for series, count in sorted(series_counts.items()):
            lines.append(f"| {series} | {count} |")
    else:
        lines.append("No non-EQ rows observed.")

    lines += ["", "## Missing Archives", ""]
    if missing_archives:
        lines += ["| Date | Reason |", "| --- | --- |"]
        for session_date, reason in missing_archives:
            lines.append(f"| {session_date} | `{reason}` |")
    else:
        lines.append("None.")

    lines += ["", "## Failed Archive Downloads Or Reuse", ""]
    if failed_archives:
        lines += ["| Date | Reason |", "| --- | --- |"]
        for session_date, reason in failed_archives:
            lines.append(f"| {session_date} | `{reason}` |")
    else:
        lines.append("None.")

    lines += ["", "## File-Level Parser Failures", ""]
    if file_failures:
        lines += ["| Date | File | Reason |", "| --- | --- | --- |"]
        for session_date, name, reason in file_failures:
            lines.append(f"| {session_date} | `{name}` | `{reason}` |")
    else:
        lines.append("None.")

    lines += ["", "## Row-Level Rejection Categories", ""]
    if rejected_reasons:
        lines += ["| Category | Count |", "| --- | ---: |"]
        for reason, count in rejected_reasons.most_common():
            lines.append(f"| {reason} | {count} |")
    else:
        lines.append("None.")

    lines += ["", "## Row-Level Rejection Examples", ""]
    if rejected_examples:
        lines += ["| Date | Row | Symbol | Series | Reason |", "| --- | ---: | --- | --- | --- |"]
        for session_date, row_number, symbol, series, reason in rejected_examples:
            lines.append(f"| {session_date} | {row_number} | `{symbol}` | `{series}` | `{reason}` |")
    else:
        lines.append("None.")

    lines += [
        "",
        "## Interpretation",
        "",
        "This scan validates the legacy parser against the actual source family used for",
        "the entire 2016-2022 research period and the 2023 to 5 July 2024 validation",
        "segment. Any missing archive, failed archive, file-level failure, or row-level",
        "rejection must be reviewed before universe selection.",
        "",
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())