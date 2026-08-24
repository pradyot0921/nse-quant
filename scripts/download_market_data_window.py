from __future__ import annotations

from datetime import date
from pathlib import Path
import argparse

from nse_quant.data.nse_acquisition import load_session_calendar
from nse_quant.data.nse_legacy_acquisition import cm_bhavcopy_archive_url
from nse_quant.data.nse_market_acquisition import (
    CM_UDIFF,
    LEGACY_CM_BHAVCOPY,
    MarketDataBatchReport,
    MarketDataDownloadProblem,
    download_market_data_files,
    market_data_raw_path,
    market_data_source_for_session,
)
from nse_quant.data.nse_acquisition import cm_udiff_archive_url


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CALENDAR = (
    PROJECT_ROOT / "data" / "calendars" / "nse_cm_sessions_2016-01-01_2026-08-19.csv"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "docs" / "validation" / "MARKET_DATA_ACQUISITION_V0.md"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", default="data/raw")
    parser.add_argument("--calendar", default=str(DEFAULT_CALENDAR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--exclude-special", action="store_true")
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--fail-on-problems", action="store_true")
    args = parser.parse_args()

    start = date.fromisoformat(args.start) if args.start else None
    end = date.fromisoformat(args.end) if args.end else None
    sessions = tuple(
        session
        for session in load_session_calendar(args.calendar)
        if (not args.exclude_special or session.session_type == "NORMAL")
        and (start is None or session.session_date >= start)
        and (end is None or session.session_date <= end)
    )

    raw_root = PROJECT_ROOT / args.raw_root
    total = len(sessions)
    print(f"Downloading/auditing {total} market-data sessions")
    print(f"raw_root={raw_root}")
    print(f"calendar={args.calendar}")
    print(f"include_special={not args.exclude_special}")

    records = []
    missing = []
    failures = []
    for index, session in enumerate(sessions, start=1):
        source = market_data_source_for_session(session.session_date)
        path = market_data_raw_path(raw_root, session.session_date)
        url = _archive_url(source, session.session_date)
        action = "reuse" if path.exists() else "download"
        print(f"{index}/{total} starting {session.session_date} {action} {url}", flush=True)

        report = download_market_data_files(
            (session,),
            raw_root,
            max_retries=args.max_retries,
            retry_delay_seconds=args.delay_seconds,
        )
        records.extend(report.records)
        missing.extend(report.missing_archives)
        failures.extend(report.failed_archives)
        print(
            f"{index}/{total} done {session.session_date}; "
            f"ok={len(records)} missing={len(missing)} failed={len(failures)}",
            flush=True,
        )

    report = MarketDataBatchReport(
        records=tuple(records),
        missing_archives=tuple(missing),
        failed_archives=tuple(failures),
    )
    output = write_acquisition_report(report, args.output, raw_root=raw_root)

    print(f"Wrote {output}")
    print(f"records={len(report.records)}")
    print(f"missing_archives={len(report.missing_archives)}")
    print(f"failed_archives={len(report.failed_archives)}")

    if args.fail_on_problems and (report.missing_archives or report.failed_archives):
        return 1
    return 0


def write_acquisition_report(
    report: MarketDataBatchReport,
    output_path: str | Path,
    *,
    raw_root: Path,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    status_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}
    for record in report.records:
        status_counts[record.status] = status_counts.get(record.status, 0) + 1
        source_counts[record.source] = source_counts.get(record.source, 0) + 1

    lines = [
        "# Market Data Acquisition V0",
        "",
        "## Scope",
        "",
        "Downloads or reuses immutable raw NSE market-data archives for the",
        "checked-in V0 session calendar. Existing archives are ZIP-validated before",
        "reuse; corrupt existing archives are deleted and re-downloaded once by the",
        "batch layer.",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Records acquired or reused | {len(report.records)} |",
        f"| Missing archives | {len(report.missing_archives)} |",
        f"| Failed archives | {len(report.failed_archives)} |",
        "",
        "## Source Counts",
        "",
        "| Source | Count |",
        "| --- | ---: |",
    ]
    lines.extend(
        f"| {source} | {source_counts[source]} |" for source in sorted(source_counts)
    )
    lines.extend(
        [
            "",
            "## Status Counts",
            "",
            "| Status | Count |",
            "| --- | ---: |",
        ]
    )
    lines.extend(
        f"| {status} | {status_counts[status]} |" for status in sorted(status_counts)
    )
    lines.extend(
        [
            "",
            "## Missing Archives",
            "",
            _problem_table(report.missing_archives, raw_root=raw_root),
            "",
            "## Failed Archives",
            "",
            _problem_table(report.failed_archives, raw_root=raw_root),
            "",
            "## Interpretation",
            "",
            "Missing or failed archives are data-quality problems that must be reviewed",
            "before universe selection. This report records raw-file availability only;",
            "row-level parser validation is performed separately by",
            "`scripts/validate_market_data_window.py`.",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def _problem_table(
    problems: tuple[MarketDataDownloadProblem, ...],
    *,
    raw_root: Path,
) -> str:
    if not problems:
        return "None."
    rows = [
        "| Date | Source | File | Reason |",
        "| --- | --- | --- | --- |",
    ]
    for problem in problems:
        path = _relative_to(problem.path, raw_root)
        rows.append(
            f"| {problem.session_date} | {problem.source} | `{path}` | "
            f"`{problem.reason}` |"
        )
    return "\n".join(rows)


def _archive_url(source: str, session_date: date) -> str:
    if source == LEGACY_CM_BHAVCOPY:
        return cm_bhavcopy_archive_url(session_date)
    if source == CM_UDIFF:
        return cm_udiff_archive_url(session_date)
    raise AssertionError(f"unsupported source {source!r}")


def _relative_to(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
