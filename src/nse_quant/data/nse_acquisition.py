"""NSE CM-UDiFF acquisition and session-calendar helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import csv
import io
from pathlib import Path
import re
import tempfile
import time
from typing import Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zipfile


CM_UDIFF_ARCHIVE_URL_TEMPLATE = (
    "https://nsearchives.nseindia.com/content/cm/"
    "BhavCopy_NSE_CM_0_0_0_{yyyymmdd}_F_0000.csv.zip"
)
SESSION_CALENDAR_COLUMNS = ("date", "session_type", "source")
COMPACT_SESSION_CALENDAR_COLUMNS = ("date", "session_type")
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; nse-quant-research/0.1; "
    "+https://github.com/pradyot0921/nse-quant)"
)


class UDiffAcquisitionError(RuntimeError):
    """Raised when a raw CM-UDiFF file cannot be acquired safely."""


class UDiffArchiveNotFoundError(UDiffAcquisitionError):
    """Raised when NSE reports that a requested CM-UDiFF archive is absent."""


class UDiffDownloadRetryableError(UDiffAcquisitionError):
    """Raised when a CM-UDiFF download failure should be retried."""


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
        fieldnames = tuple(reader.fieldnames or ())
        if fieldnames not in {
            SESSION_CALENDAR_COLUMNS,
            COMPACT_SESSION_CALENDAR_COLUMNS,
        }:
            raise TradingCalendarError(
                f"{source.name}: unexpected columns {reader.fieldnames!r}"
            )

        rows = tuple(enumerate(reader, start=2))
        if (
            fieldnames == COMPACT_SESSION_CALENDAR_COLUMNS
            and any(
                row["session_type"].strip().upper() in {"START", "END", "H"}
                for _, row in rows
            )
        ):
            return _load_compact_session_calendar(source.name, rows)

        sessions = []
        seen_dates: set[date] = set()
        for row_number, row in rows:
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
            if session_type == "N":
                session_type = "NORMAL"
            elif session_type == "S":
                session_type = "SPECIAL"
            source_note = row.get("source", "").strip()
            if not source_note and fieldnames == COMPACT_SESSION_CALENDAR_COLUMNS:
                source_note = "COMPACT_CALENDAR"
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


def _load_compact_session_calendar(
    source_name: str,
    rows: tuple[tuple[int, dict[str, str]], ...],
) -> tuple[TradingSession, ...]:
    start_date = None
    end_date = None
    holidays: set[date] = set()
    special_dates: set[date] = set()

    for row_number, row in rows:
        try:
            session_date = date.fromisoformat(row["date"].strip())
        except ValueError:
            raise TradingCalendarError(
                f"{source_name}:{row_number}: date is not ISO formatted"
            ) from None

        session_type = row["session_type"].strip().upper()
        if session_type == "START":
            if start_date is not None:
                raise TradingCalendarError(
                    f"{source_name}:{row_number}: duplicate START"
                )
            start_date = session_date
        elif session_type == "END":
            if end_date is not None:
                raise TradingCalendarError(
                    f"{source_name}:{row_number}: duplicate END"
                )
            end_date = session_date
        elif session_type == "H":
            holidays.add(session_date)
        elif session_type == "S":
            special_dates.add(session_date)
        else:
            raise TradingCalendarError(
                f"{source_name}:{row_number}: unsupported session_type {session_type!r}"
            )

    if start_date is None or end_date is None:
        raise TradingCalendarError(f"{source_name}: START and END are required")
    if end_date < start_date:
        raise TradingCalendarError(f"{source_name}: END is before START")

    sessions = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5 and current not in holidays:
            sessions.append(TradingSession(current, "NORMAL", "COMPACT_CALENDAR"))
        current += timedelta(days=1)

    existing_dates = {session.session_date for session in sessions}
    for special_date in sorted(special_dates):
        if special_date in existing_dates:
            raise TradingCalendarError(
                f"{source_name}: special session overlaps normal session {special_date}"
            )
        if not start_date <= special_date <= end_date:
            raise TradingCalendarError(
                f"{source_name}: special session outside window {special_date}"
            )
        sessions.append(TradingSession(special_date, "SPECIAL", "COMPACT_CALENDAR"))

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


def research_sessions(
    sessions: Iterable[TradingSession],
    *,
    include_special: bool = False,
) -> tuple[TradingSession, ...]:
    """Return sessions eligible for research bars.

    Special sessions remain in the calendar for raw-file auditing but are
    excluded from the V0 research bar series unless explicitly requested.
    """

    return tuple(
        session
        for session in sessions
        if include_special or session.session_type == "NORMAL"
    )


def download_cm_udiff_file(
    session_date: date,
    raw_root: str | Path,
    *,
    fetch_bytes: Callable[[str], bytes] | None = None,
    max_retries: int = 3,
    retry_delay_seconds: float = 1.0,
) -> Path:
    """Download one CM-UDiFF ZIP to immutable raw storage."""

    destination = cm_udiff_raw_path(raw_root, session_date)
    if destination.exists():
        _validate_single_csv_zip(
            destination.read_bytes(),
            archive_name=destination.name,
        )
        return destination

    fetcher = fetch_bytes or _fetch_url
    url = cm_udiff_archive_url(session_date)
    content = _fetch_with_retries(
        url,
        fetcher=fetcher,
        max_retries=max_retries,
        retry_delay_seconds=retry_delay_seconds,
    )
    _validate_single_csv_zip(content, archive_name=destination.name)

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


def _fetch_with_retries(
    url: str,
    *,
    fetcher: Callable[[str], bytes],
    max_retries: int,
    retry_delay_seconds: float,
) -> bytes:
    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")
    if retry_delay_seconds < 0:
        raise ValueError("retry_delay_seconds must be non-negative")

    attempts = max_retries + 1
    for attempt in range(1, attempts + 1):
        try:
            return fetcher(url)
        except UDiffArchiveNotFoundError:
            raise
        except UDiffDownloadRetryableError:
            if attempt == attempts:
                raise
            time.sleep(retry_delay_seconds)

    raise AssertionError("unreachable retry loop exit")


def _validate_single_csv_zip(content: bytes, *, archive_name: str) -> None:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            csv_names = [
                name for name in archive.namelist() if name.lower().endswith(".csv")
            ]
            if len(csv_names) != 1:
                raise UDiffAcquisitionError(
                    f"{archive_name}: expected exactly one CSV in ZIP, "
                    f"found {len(csv_names)}"
                )
            corrupt_member = archive.testzip()
            if corrupt_member is not None:
                raise UDiffAcquisitionError(
                    f"{archive_name}: corrupt ZIP member {corrupt_member}"
                )
    except zipfile.BadZipFile:
        raise UDiffAcquisitionError(
            f"{archive_name}: downloaded content is not a ZIP archive"
        ) from None


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
    except HTTPError as exc:
        if exc.code == 404:
            raise UDiffArchiveNotFoundError(f"archive not found: {url}") from exc
        if 500 <= exc.code <= 599:
            raise UDiffDownloadRetryableError(
                f"temporary NSE archive error {exc.code}: {url}"
            ) from exc
        raise UDiffAcquisitionError(f"NSE archive error {exc.code}: {url}") from exc
    except URLError as exc:
        raise UDiffDownloadRetryableError(f"failed to download {url}: {exc}") from exc
