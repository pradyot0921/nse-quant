"""Batch acquisition orchestration for NSE daily market-data archives.

Per-file download primitives stay in their source-specific modules. This
module chooses the correct source family for each checked-in trading session
and records batch outcomes without silently changing raw data policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Iterable

from nse_quant.data.nse_acquisition import (
    TradingSession,
    UDiffAcquisitionError,
    UDiffArchiveNotFoundError,
    cm_udiff_raw_path,
    date_from_cm_udiff_filename,
    download_cm_udiff_file,
)
from nse_quant.data.nse_legacy_acquisition import (
    LegacyBhavcopyAcquisitionError,
    LegacyBhavcopyArchiveNotFoundError,
    cm_bhavcopy_raw_path,
    date_from_cm_bhavcopy_filename,
    download_cm_bhavcopy_file,
)


LEGACY_CM_BHAVCOPY = "legacy_cm_bhavcopy"
CM_UDIFF = "cm_udiff"
LEGACY_LAST_SESSION = date(2024, 7, 5)
UDIFF_FIRST_SESSION = date(2024, 7, 8)


class MarketDataAcquisitionError(RuntimeError):
    """Raised when a batch market-data acquisition request is invalid."""


@dataclass(frozen=True)
class MarketDataDownloadRecord:
    session_date: date
    source: str
    path: Path
    status: str


@dataclass(frozen=True)
class MarketDataDownloadProblem:
    session_date: date
    source: str
    path: Path
    reason: str


@dataclass(frozen=True)
class MarketDataBatchReport:
    records: tuple[MarketDataDownloadRecord, ...]
    missing_archives: tuple[MarketDataDownloadProblem, ...]
    failed_archives: tuple[MarketDataDownloadProblem, ...]


@dataclass(frozen=True)
class MarketDataRawFileAudit:
    expected_files: tuple[Path, ...]
    missing_files: tuple[Path, ...]
    unexpected_files: tuple[Path, ...]


def market_data_source_for_session(session_date: date) -> str:
    """Return the registered V0 source family for one trading session."""

    if session_date <= LEGACY_LAST_SESSION:
        return LEGACY_CM_BHAVCOPY
    if session_date >= UDIFF_FIRST_SESSION:
        return CM_UDIFF
    raise MarketDataAcquisitionError(
        f"{session_date}: no registered daily-market source; "
        "special sessions in the 6-7 July 2024 transition gap need an "
        "explicit source decision"
    )


def market_data_raw_path(raw_root: str | Path, session_date: date) -> Path:
    """Return the immutable raw archive path for one V0 trading session."""

    source = market_data_source_for_session(session_date)
    if source == LEGACY_CM_BHAVCOPY:
        return cm_bhavcopy_raw_path(raw_root, session_date)
    return cm_udiff_raw_path(raw_root, session_date)


def download_market_data_files(
    sessions: Iterable[TradingSession],
    raw_root: str | Path,
    *,
    legacy_fetch_bytes: Callable[[str], bytes] | None = None,
    udiff_fetch_bytes: Callable[[str], bytes] | None = None,
    max_retries: int = 3,
    retry_delay_seconds: float = 1.0,
    redownload_invalid_existing: bool = True,
) -> MarketDataBatchReport:
    """Download expected NSE daily archives and collect all batch outcomes.

    A 404 for an expected session is recorded and the batch continues. If an
    existing archive fails source-specific ZIP validation, the batch deletes it,
    re-downloads once, and records the repair or final failure.
    """

    root = Path(raw_root)
    records: list[MarketDataDownloadRecord] = []
    missing: list[MarketDataDownloadProblem] = []
    failures: list[MarketDataDownloadProblem] = []

    for session in sessions:
        session_date = session.session_date
        source = market_data_source_for_session(session_date)
        path = market_data_raw_path(root, session_date)
        existed_before = path.exists()

        try:
            result = _download_for_source(
                source,
                session_date,
                root,
                legacy_fetch_bytes=legacy_fetch_bytes,
                udiff_fetch_bytes=udiff_fetch_bytes,
                max_retries=max_retries,
                retry_delay_seconds=retry_delay_seconds,
            )
        except (LegacyBhavcopyArchiveNotFoundError, UDiffArchiveNotFoundError) as exc:
            missing.append(_problem(session_date, source, path, exc))
            continue
        except (LegacyBhavcopyAcquisitionError, UDiffAcquisitionError) as exc:
            if not existed_before or not redownload_invalid_existing:
                failures.append(_problem(session_date, source, path, exc))
                continue

            if not _delete_existing_archive(path, root):
                failures.append(
                    MarketDataDownloadProblem(
                        session_date=session_date,
                        source=source,
                        path=path,
                        reason=f"{exc}; refused to delete path outside raw root",
                    )
                )
                continue

            try:
                result = _download_for_source(
                    source,
                    session_date,
                    root,
                    legacy_fetch_bytes=legacy_fetch_bytes,
                    udiff_fetch_bytes=udiff_fetch_bytes,
                    max_retries=0,
                    retry_delay_seconds=retry_delay_seconds,
                )
            except (
                LegacyBhavcopyArchiveNotFoundError,
                UDiffArchiveNotFoundError,
            ) as retry_exc:
                missing.append(_problem(session_date, source, path, retry_exc))
                continue
            except (LegacyBhavcopyAcquisitionError, UDiffAcquisitionError) as retry_exc:
                failures.append(_problem(session_date, source, path, retry_exc))
                continue

            records.append(
                MarketDataDownloadRecord(
                    session_date=session_date,
                    source=source,
                    path=result,
                    status="redownloaded",
                )
            )
            continue

        records.append(
            MarketDataDownloadRecord(
                session_date=session_date,
                source=source,
                path=result,
                status="reused" if existed_before else "downloaded",
            )
        )

    return MarketDataBatchReport(
        records=tuple(records),
        missing_archives=tuple(missing),
        failed_archives=tuple(failures),
    )


def audit_market_data_raw_files(
    raw_root: str | Path,
    sessions: Iterable[TradingSession],
) -> MarketDataRawFileAudit:
    """Compare raw archives on disk with the checked-in session calendar."""

    root = Path(raw_root)
    expected_files = tuple(
        market_data_raw_path(root, session.session_date) for session in sessions
    )
    expected_set = {_resolved(path) for path in expected_files}
    observed_files = tuple(
        sorted(_observed_legacy_archives(root) + _observed_udiff_archives(root))
    )
    observed_set = {_resolved(path) for path in observed_files}

    return MarketDataRawFileAudit(
        expected_files=expected_files,
        missing_files=tuple(
            path for path in expected_files if _resolved(path) not in observed_set
        ),
        unexpected_files=tuple(
            path for path in observed_files if _resolved(path) not in expected_set
        ),
    )


def _download_for_source(
    source: str,
    session_date: date,
    raw_root: Path,
    *,
    legacy_fetch_bytes: Callable[[str], bytes] | None,
    udiff_fetch_bytes: Callable[[str], bytes] | None,
    max_retries: int,
    retry_delay_seconds: float,
) -> Path:
    if source == LEGACY_CM_BHAVCOPY:
        return download_cm_bhavcopy_file(
            session_date,
            raw_root,
            fetch_bytes=legacy_fetch_bytes,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
        )
    if source == CM_UDIFF:
        return download_cm_udiff_file(
            session_date,
            raw_root,
            fetch_bytes=udiff_fetch_bytes,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
        )
    raise MarketDataAcquisitionError(f"unsupported market-data source {source!r}")


def _problem(
    session_date: date,
    source: str,
    path: Path,
    exc: Exception,
) -> MarketDataDownloadProblem:
    return MarketDataDownloadProblem(
        session_date=session_date,
        source=source,
        path=path,
        reason=str(exc),
    )


def _delete_existing_archive(path: Path, raw_root: Path) -> bool:
    resolved_path = _resolved(path)
    resolved_root = _resolved(raw_root)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        return False
    if path.exists():
        path.unlink()
    return True


def _observed_legacy_archives(raw_root: Path) -> list[Path]:
    root = raw_root / "nse" / "cm_bhavcopy"
    return [
        path
        for path in root.glob("**/cm*bhav.csv.zip")
        if date_from_cm_bhavcopy_filename(path.name) is not None
    ]


def _observed_udiff_archives(raw_root: Path) -> list[Path]:
    root = raw_root / "nse" / "cm_udiff"
    return [
        path
        for path in root.glob("**/BhavCopy_NSE_CM_0_0_0_*_F_0000.csv.zip")
        if date_from_cm_udiff_filename(path.name) is not None
    ]


def _resolved(path: Path) -> Path:
    return path.resolve(strict=False)
