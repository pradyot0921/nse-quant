"""Offline validation for raw NSE daily market-data archives.

This layer does not download data. It audits checked-in expected sessions
against raw files on disk, parses the expected source family for each research
session, and exposes canonical bars plus explicit validation problems.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

from nse_quant.data.market_data_bars import (
    CanonicalEquityBar,
    canonical_bar_from_legacy,
    canonical_bar_from_udiff,
)
from nse_quant.data.nse_acquisition import (
    TradingSession,
    date_from_cm_udiff_filename,
    research_sessions,
)
from nse_quant.data.nse_legacy_bhavcopy import (
    LegacyBhavcopyParseError,
    parse_cm_bhavcopy_file,
)
from nse_quant.data.nse_legacy_acquisition import date_from_cm_bhavcopy_filename
from nse_quant.data.nse_market_acquisition import (
    CM_UDIFF,
    LEGACY_CM_BHAVCOPY,
    audit_market_data_raw_files,
    market_data_raw_path,
    market_data_source_for_session,
)
from nse_quant.data.nse_udiff import UDiffParseError, parse_cm_udiff_file


@dataclass(frozen=True)
class MarketDataSessionValidation:
    session_date: date
    source: str
    path: Path
    status: str
    bar_count: int
    rejected_row_count: int


@dataclass(frozen=True)
class MarketDataFileProblem:
    session_date: date | None
    source: str
    path: Path
    reason: str


@dataclass(frozen=True)
class MarketDataRejectedRow:
    session_date: date
    source: str
    row_number: int
    symbol: str
    series: str
    reason: str


@dataclass(frozen=True)
class MarketDataValidationReport:
    sessions_checked: tuple[TradingSession, ...]
    research_sessions_checked: tuple[TradingSession, ...]
    records: tuple[MarketDataSessionValidation, ...]
    bars: tuple[CanonicalEquityBar, ...]
    missing_files: tuple[MarketDataFileProblem, ...]
    unexpected_files: tuple[MarketDataFileProblem, ...]
    file_failures: tuple[MarketDataFileProblem, ...]
    rejected_rows: tuple[MarketDataRejectedRow, ...]
    non_eq_series_counts: dict[str, int]

    @property
    def has_blocking_problems(self) -> bool:
        return bool(self.missing_files or self.file_failures or self.rejected_rows)


def validate_market_data_files(
    raw_root: str | Path,
    sessions: Iterable[TradingSession],
    *,
    include_special: bool = False,
) -> MarketDataValidationReport:
    """Validate local raw archives and parse expected research bars.

    Raw-file auditing always uses every supplied session, including special
    sessions. Research-bar parsing excludes special sessions by default per
    D-029 unless `include_special=True`.
    """

    root = Path(raw_root)
    session_tuple = tuple(sessions)
    research_session_tuple = research_sessions(
        session_tuple,
        include_special=include_special,
    )
    raw_audit = audit_market_data_raw_files(root, session_tuple)
    missing_paths = {_resolved(path) for path in raw_audit.missing_files}
    unexpected_paths = tuple(
        path
        for path in raw_audit.unexpected_files
        if _path_is_inside_session_window(path, session_tuple)
    )

    records: list[MarketDataSessionValidation] = []
    bars: list[CanonicalEquityBar] = []
    file_failures: list[MarketDataFileProblem] = []
    rejected_rows: list[MarketDataRejectedRow] = []
    non_eq_series_counts = Counter()

    for session in research_session_tuple:
        session_date = session.session_date
        source = market_data_source_for_session(session_date)
        path = market_data_raw_path(root, session_date)

        if _resolved(path) in missing_paths:
            records.append(
                MarketDataSessionValidation(
                    session_date=session_date,
                    source=source,
                    path=path,
                    status="missing_file",
                    bar_count=0,
                    rejected_row_count=0,
                )
            )
            continue

        try:
            parsed_bars, parsed_rejections, parsed_series_counts = _parse_expected_file(
                path,
                source=source,
                session_date=session_date,
            )
        except (LegacyBhavcopyParseError, UDiffParseError) as exc:
            file_failures.append(
                MarketDataFileProblem(
                    session_date=session_date,
                    source=source,
                    path=path,
                    reason=str(exc),
                )
            )
            records.append(
                MarketDataSessionValidation(
                    session_date=session_date,
                    source=source,
                    path=path,
                    status="file_failed",
                    bar_count=0,
                    rejected_row_count=0,
                )
            )
            continue

        bars.extend(parsed_bars)
        rejected_rows.extend(parsed_rejections)
        non_eq_series_counts.update(parsed_series_counts)
        records.append(
            MarketDataSessionValidation(
                session_date=session_date,
                source=source,
                path=path,
                status="parsed",
                bar_count=len(parsed_bars),
                rejected_row_count=len(parsed_rejections),
            )
        )

    return MarketDataValidationReport(
        sessions_checked=session_tuple,
        research_sessions_checked=research_session_tuple,
        records=tuple(records),
        bars=tuple(bars),
        missing_files=tuple(
            _problem_from_path(path, reason="expected raw archive is missing")
            for path in raw_audit.missing_files
        ),
        unexpected_files=tuple(
            _problem_from_path(path, reason="raw archive is not expected")
            for path in unexpected_paths
        ),
        file_failures=tuple(file_failures),
        rejected_rows=tuple(rejected_rows),
        non_eq_series_counts=dict(sorted(non_eq_series_counts.items())),
    )


def write_market_data_validation_report(
    report: MarketDataValidationReport,
    output_path: str | Path,
    *,
    raw_root: str | Path,
) -> Path:
    """Write a Markdown validation report for a market-data build attempt."""

    output = Path(output_path)
    raw_root_path = Path(raw_root)
    status_counts = Counter(record.status for record in report.records)
    source_counts = Counter(record.source for record in report.records)

    lines = [
        "# Market Data Validation Report V0",
        "",
        "**Status:** Evidence artifact",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Calendar sessions checked | {len(report.sessions_checked)} |",
        f"| Research sessions parsed/attempted | {len(report.research_sessions_checked)} |",
        f"| Parsed session files | {status_counts['parsed']} |",
        f"| Missing expected raw files | {len(report.missing_files)} |",
        f"| Unexpected raw files | {len(report.unexpected_files)} |",
        f"| File-level parser failures | {len(report.file_failures)} |",
        f"| Row-level rejections | {len(report.rejected_rows)} |",
        f"| Canonical bars emitted | {len(report.bars)} |",
        "",
        "## Source Records",
        "",
        "| Source | Sessions |",
        "| --- | ---: |",
    ]
    for source, count in sorted(source_counts.items()):
        lines.append(f"| {source} | {count} |")

    lines += [
        "",
        "## Session Results",
        "",
        "| Date | Source | Status | Bars | Rejected rows |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for record in report.records:
        lines.append(
            f"| {record.session_date} | {record.source} | {record.status} | "
            f"{record.bar_count} | {record.rejected_row_count} |"
        )

    _append_problem_table(
        lines,
        "Missing Expected Raw Files",
        report.missing_files,
        raw_root=raw_root_path,
    )
    _append_problem_table(
        lines,
        "Unexpected Raw Files",
        report.unexpected_files,
        raw_root=raw_root_path,
    )
    _append_problem_table(
        lines,
        "File-Level Parser Failures",
        report.file_failures,
        raw_root=raw_root_path,
    )
    _append_rejected_rows(lines, report.rejected_rows)
    _append_non_eq_series(lines, report.non_eq_series_counts)

    lines += [
        "",
        "## Interpretation",
        "",
        "This report is an offline validation artifact. It does not download raw",
        "archives and does not freeze the V0 universe. Missing files, parser",
        "failures, and rejected EQ rows remain explicit inputs to the later",
        "dataset-builder and universe-selection gates.",
        "",
    ]

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def _parse_expected_file(
    path: Path,
    *,
    source: str,
    session_date: date,
) -> tuple[tuple[CanonicalEquityBar, ...], tuple[MarketDataRejectedRow, ...], dict[str, int]]:
    if source == LEGACY_CM_BHAVCOPY:
        parsed = parse_cm_bhavcopy_file(path)
        return (
            tuple(canonical_bar_from_legacy(bar) for bar in parsed.bars),
            tuple(
                MarketDataRejectedRow(
                    session_date=session_date,
                    source=source,
                    row_number=row.row_number,
                    symbol=row.symbol,
                    series=row.series,
                    reason=row.reason,
                )
                for row in parsed.rejected_rows
            ),
            parsed.rejected_series_counts,
        )

    if source == CM_UDIFF:
        parsed = parse_cm_udiff_file(path)
        return (
            tuple(canonical_bar_from_udiff(bar) for bar in parsed.bars),
            tuple(
                MarketDataRejectedRow(
                    session_date=session_date,
                    source=source,
                    row_number=row.row_number,
                    symbol=row.symbol,
                    series=row.series,
                    reason=row.reason,
                )
                for row in parsed.rejected_rows
            ),
            parsed.rejected_series_counts,
        )

    raise ValueError(f"unsupported market-data source {source!r}")


def _problem_from_path(path: Path, *, reason: str) -> MarketDataFileProblem:
    session_date, source = _path_date_and_source(path)

    return MarketDataFileProblem(
        session_date=session_date,
        source=source,
        path=path,
        reason=reason,
    )


def _path_is_inside_session_window(
    path: Path,
    sessions: tuple[TradingSession, ...],
) -> bool:
    if not sessions:
        return False

    session_date, _ = _path_date_and_source(path)
    if session_date is None:
        return True

    session_dates = tuple(session.session_date for session in sessions)
    return min(session_dates) <= session_date <= max(session_dates)


def _path_date_and_source(path: Path) -> tuple[date | None, str]:
    legacy_date = date_from_cm_bhavcopy_filename(path.name)
    if legacy_date is not None:
        return legacy_date, LEGACY_CM_BHAVCOPY

    udiff_date = date_from_cm_udiff_filename(path.name)
    if udiff_date is not None:
        return udiff_date, CM_UDIFF

    return None, "unknown"


def _append_problem_table(
    lines: list[str],
    title: str,
    problems: tuple[MarketDataFileProblem, ...],
    *,
    raw_root: Path,
) -> None:
    lines += ["", f"## {title}", ""]
    if not problems:
        lines.append("None.")
        return

    lines += ["| Date | Source | Path | Reason |", "| --- | --- | --- | --- |"]
    for problem in problems:
        lines.append(
            f"| {problem.session_date or ''} | {problem.source} | "
            f"`{_display_path(problem.path, raw_root)}` | `{problem.reason}` |"
        )


def _append_rejected_rows(
    lines: list[str],
    rejected_rows: tuple[MarketDataRejectedRow, ...],
) -> None:
    lines += ["", "## Row-Level Rejections", ""]
    if not rejected_rows:
        lines.append("None.")
        return

    lines += [
        "| Date | Source | Row | Symbol | Series | Reason |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for row in rejected_rows[:100]:
        lines.append(
            f"| {row.session_date} | {row.source} | {row.row_number} | "
            f"`{row.symbol}` | `{row.series}` | `{row.reason}` |"
        )
    if len(rejected_rows) > 100:
        lines.append(f"| ... | ... | ... | ... | ... | {len(rejected_rows) - 100} more |")


def _append_non_eq_series(lines: list[str], series_counts: dict[str, int]) -> None:
    lines += ["", "## Non-EQ Series Counts", ""]
    if not series_counts:
        lines.append("None.")
        return

    lines += ["| Series | Rows |", "| --- | ---: |"]
    for series, count in series_counts.items():
        lines.append(f"| {series} | {count} |")


def _display_path(path: Path, raw_root: Path) -> str:
    try:
        return str(path.resolve(strict=False).relative_to(raw_root.resolve(strict=False)))
    except ValueError:
        return str(path)


def _resolved(path: Path) -> Path:
    return path.resolve(strict=False)
