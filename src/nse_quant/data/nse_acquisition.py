"""NSE CM-UDiFF acquisition and session-calendar helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import csv
from pathlib import Path
import re
import tempfile
from typing import Callable, Iterable
from urllib.request import Request, urlopen


CM_UDIFF_ARCHIVE_URL_TEMPLATE = (
    "https://nsearchives.nseindia.com/content/cm/"
    "BhavCopy_NSE_CM_0_0_0_{yyyymmdd}_F_0000.csv.zip"
)
SESSION_CALENDAR_COLUMNS = ("date", "session_type", "source")
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; nse-quant-research/0.1; "
    "+https://github.com/pradyot0921/nse-quant)"
)


class UDiffAcquisitionError(RuntimeError):
    """Raised when a raw CM-UDiFF file cannot be acquired safely."""


class TradingCalendarError(ValueError):
    """Raised when a checked-in trading-session calendar is invalid."""


@dataclass(frozen=True)
class TradingSession:
    session_date: date
    session_type: str
    source: str


@dataclass(frozen=True)
class RawFileAudit:
    expected_files: tuple[Path, ...]
    missing_files: tuple[Path, ...]
    unexpected_files: tuple[Path, ...]


def cm_udiff_filename(session_date: date) -> str:
    """Return NSE's canonical CM-UDiFF archive name for one session."""

    return f"BhavCopy_NSE_CM_0_0_0_{session_date:%Y%m%d}_F_0000.csv.zip"


def cm_udiff_archive_url(session_date: date) -> str:
    """Return NSE's public archive URL for one CM-UDiFF session file."""

    return CM_UDIFF_ARCHIVE_URL_TEMPLATE.format(yyyymmdd=f"{session_date:%Y%m%d}")


def cm_udiff_raw_path(raw_root: str | Path, session_date: date) -> Path:
    """Return the immutable raw-storage path for one CM-UDiFF archive."""

    root = Path(raw_root)
    return (
        root
        / "nse"
        / "cm_udiff"
        / f"{session_date:%Y}"
        / f"{session_date:%m}"
        / cm_udiff_filename(session_date)
    )


def load_session_calendar(path: str | Path) -> tuple[TradingSession, ...]:
    """Load a checked-in NSE Capital Market trading-session calendar."""

    source = Path(path)
    with source.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != SESSION_CALENDAR_COLUMNS:
            raise TradingCalendarError(
                f"{source.name}: unexpected columns {reader.fieldnames!r}"
            )

        sessions = []
        seen_dates: set[date] = set()
        for row_number, row in enumerate(reader, start=2):
            try:
                session_date = date.fromisoformat(row["date"].strip())
            except ValueError:
                raise TradingCalendarError(
                    f"{source.name}:{row_number}: date is not ISO formatted"
                ) from None

            if session_date in seen_dates:
                raise TradingCalendarError(
                    f"{source.name}:{row_number}: duplicate session {session_date}"
                )

            session_type = row["session_type"].strip().upper()
            source_note = row["source"].strip()
            if session_type not in {"NORMAL", "SPECIAL"}:
                raise TradingCalendarError(
                    f"{source.name}:{row_number}: unsupported session_type {session_type!r}"
                )
            if not source_note:
                raise TradingCalendarError(
                    f"{source.name}:{row_number}: source is required"
                )

            seen_dates.add(session_date)
            sessions.append(
                TradingSession(
                    session_date=session_date,
                    session_type=session_type,
                    source=source_note,
                )
            )

    return tuple(sorted(sessions, key=lambda session: session.session_date))


def audit_cm_udiff_raw_files(
    raw_root: str | Path,
    sessions: Iterable[TradingSession],
) -> RawFileAudit:
    """Compare raw CM-UDiFF files on disk with the expected session calendar."""

    session_tuple = tuple(sessions)
    expected_files = tuple(
        cm_udiff_raw_path(raw_root, session.session_date) for session in session_tuple
    )
    expected_set = {path.resolve() for path in expected_files}

    root = Path(raw_root) / "nse" / "cm_udiff"
    observed = tuple(sorted(root.glob("**/BhavCopy_NSE_CM_0_0_0_*_F_0000.csv.zip")))
    observed_set = {path.resolve() for path in observed}

    return RawFileAudit(
        expected_files=expected_files,
        missing_files=tuple(
            path for path in expected_files if path.resolve() not in observed_set
        ),
        unexpected_files=tuple(
            path for path in observed if path.resolve() not in expected_set
        ),
    )


def download_cm_udiff_file(
    session_date: date,
    raw_root: str | Path,
    *,
    overwrite: bool = False,
    fetch_bytes: Callable[[str], bytes] | None = None,
) -> Path:
    """Download one CM-UDiFF ZIP to immutable raw storage."""

    destination = cm_udiff_raw_path(raw_root, session_date)
    if destination.exists() and not overwrite:
        return destination

    fetcher = fetch_bytes or _fetch_url
    content = fetcher(cm_udiff_archive_url(session_date))
    if not content.startswith(b"PK"):
        raise UDiffAcquisitionError(
            f"{destination.name}: downloaded content is not a ZIP archive"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=destination.parent,
        delete=False,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    ) as handle:
        temp_path = Path(handle.name)
        handle.write(content)

    temp_path.replace(destination)
    return destination


def date_from_cm_udiff_filename(name: str) -> date | None:
    """Extract a session date from a canonical CM-UDiFF archive name."""

    match = re.fullmatch(r"BhavCopy_NSE_CM_0_0_0_(\d{8})_F_0000\.csv\.zip", name)
    if match is None:
        return None
    raw = match.group(1)
    return date(int(raw[:4]), int(raw[4:6]), int(raw[6:]))


def _fetch_url(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/zip,*/*",
            "Referer": "https://www.nseindia.com/all-reports",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            return response.read()
    except OSError as exc:
        raise UDiffAcquisitionError(f"failed to download {url}: {exc}") from exc
