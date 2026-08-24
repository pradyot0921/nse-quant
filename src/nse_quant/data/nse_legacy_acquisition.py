"""NSE legacy CM bhavcopy acquisition helpers.

This module downloads the pre-UDiFF `CM - Bhavcopy(csv)` ZIP files documented
in `docs/validation/LEGACY_CM_BHAVCOPY_FORMAT_SCAN_V0.md`. Parsing remains in
`nse_legacy_bhavcopy.py`; this module only resolves names, paths, URLs, and raw
archive storage.
"""

from __future__ import annotations

from datetime import date
import io
from pathlib import Path
import re
import tempfile
import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zipfile


LEGACY_CM_BHAVCOPY_ARCHIVE_URL_TEMPLATE = (
    "https://nsearchives.nseindia.com/content/historical/EQUITIES/"
    "{yyyy}/{mmm}/cm{dd}{mmm}{yyyy}bhav.csv.zip"
)
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; nse-quant-research/0.1; "
    "+https://github.com/pradyot0921/nse-quant)"
)
MONTH_ABBREVIATIONS = (
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC",
)


class LegacyBhavcopyAcquisitionError(RuntimeError):
    """Raised when a raw legacy CM bhavcopy file cannot be acquired safely."""


class LegacyBhavcopyArchiveNotFoundError(LegacyBhavcopyAcquisitionError):
    """Raised when NSE reports that a requested legacy archive is absent."""


class LegacyBhavcopyDownloadRetryableError(LegacyBhavcopyAcquisitionError):
    """Raised when a legacy CM bhavcopy download failure should be retried."""


def cm_bhavcopy_filename(session_date: date) -> str:
    """Return NSE's canonical legacy CM bhavcopy archive name for one session."""

    month = MONTH_ABBREVIATIONS[session_date.month - 1]
    return f"cm{session_date:%d}{month}{session_date:%Y}bhav.csv.zip"


def cm_bhavcopy_archive_url(session_date: date) -> str:
    """Return NSE's public legacy CM bhavcopy archive URL for one session file."""

    month = MONTH_ABBREVIATIONS[session_date.month - 1]
    return LEGACY_CM_BHAVCOPY_ARCHIVE_URL_TEMPLATE.format(
        yyyy=f"{session_date:%Y}",
        mmm=month,
        dd=f"{session_date:%d}",
    )


def cm_bhavcopy_raw_path(raw_root: str | Path, session_date: date) -> Path:
    """Return the immutable raw-storage path for one legacy CM bhavcopy archive."""

    root = Path(raw_root)
    return (
        root
        / "nse"
        / "cm_bhavcopy"
        / f"{session_date:%Y}"
        / f"{session_date:%m}"
        / cm_bhavcopy_filename(session_date)
    )


def date_from_cm_bhavcopy_filename(name: str) -> date | None:
    """Extract a session date from a canonical legacy CM bhavcopy archive name."""

    match = re.fullmatch(
        r"cm(\d{2})([A-Z]{3})(\d{4})bhav\.csv\.zip",
        name,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None

    day, month, year = match.groups()
    month = month.upper()
    if month not in MONTH_ABBREVIATIONS:
        return None

    try:
        return date(int(year), MONTH_ABBREVIATIONS.index(month) + 1, int(day))
    except ValueError:
        return None


def download_cm_bhavcopy_file(
    session_date: date,
    raw_root: str | Path,
    *,
    fetch_bytes: Callable[[str], bytes] | None = None,
    max_retries: int = 3,
    retry_delay_seconds: float = 1.0,
) -> Path:
    """Download one legacy CM bhavcopy ZIP to immutable raw storage."""

    destination = cm_bhavcopy_raw_path(raw_root, session_date)
    if destination.exists():
        _validate_single_csv_zip(destination.read_bytes(), archive_name=destination.name)
        return destination

    fetcher = fetch_bytes or _fetch_url
    url = cm_bhavcopy_archive_url(session_date)
    content = _fetch_with_retries(
        url,
        fetcher=fetcher,
        max_retries=max_retries,
        retry_delay_seconds=retry_delay_seconds,
    )
    _validate_single_csv_zip(content, archive_name=destination.name)

    destination.parent.mkdir(parents=True, exist_ok=True)
    _write_atomic(destination, content)
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
        except TimeoutError as exc:
            if attempt == attempts:
                raise LegacyBhavcopyDownloadRetryableError(
                    f"timed out downloading {url}: {exc}"
                ) from exc
            time.sleep(retry_delay_seconds)
        except LegacyBhavcopyArchiveNotFoundError:
            raise
        except LegacyBhavcopyDownloadRetryableError:
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
                raise LegacyBhavcopyAcquisitionError(
                    f"{archive_name}: expected exactly one CSV in ZIP, "
                    f"found {len(csv_names)}"
                )
            corrupt_member = archive.testzip()
            if corrupt_member is not None:
                raise LegacyBhavcopyAcquisitionError(
                    f"{archive_name}: corrupt ZIP member {corrupt_member}"
                )
    except zipfile.BadZipFile:
        raise LegacyBhavcopyAcquisitionError(
            f"{archive_name}: downloaded content is not a ZIP archive"
        ) from None


def _write_atomic(destination: Path, content: bytes) -> None:
    with tempfile.NamedTemporaryFile(
        dir=destination.parent,
        delete=False,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    ) as handle:
        temp_path = Path(handle.name)
        handle.write(content)

    temp_path.replace(destination)


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
            raise LegacyBhavcopyArchiveNotFoundError(
                f"archive not found: {url}"
            ) from exc
        if 500 <= exc.code <= 599:
            raise LegacyBhavcopyDownloadRetryableError(
                f"temporary NSE archive error {exc.code}: {url}"
            ) from exc
        raise LegacyBhavcopyAcquisitionError(
            f"NSE archive error {exc.code}: {url}"
        ) from exc
    except URLError as exc:
        raise LegacyBhavcopyDownloadRetryableError(
            f"failed to download {url}: {exc}"
        ) from exc
