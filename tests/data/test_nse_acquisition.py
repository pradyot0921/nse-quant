from datetime import date
from pathlib import Path
import zipfile

import pytest

from nse_quant.data.nse_acquisition import (
    TradingCalendarError,
    TradingSession,
    UDiffAcquisitionError,
    audit_cm_udiff_raw_files,
    cm_udiff_archive_url,
    cm_udiff_filename,
    cm_udiff_raw_path,
    date_from_cm_udiff_filename,
    download_cm_udiff_file,
    load_session_calendar,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CALENDAR_PATH = (
    PROJECT_ROOT
    / "data"
    / "calendars"
    / "nse_cm_sessions_2025-08-20_2026-08-19.csv"
)


def write_calendar(path, rows):
    path.write_text(
        "date,session_type,source\n"
        + "\n".join(
            f"{date_},{session_type},{source}" for date_, session_type, source in rows
        )
        + "\n",
        encoding="utf-8",
    )


def zip_bytes():
    import io

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("sample.csv", "TradDt\n2025-10-31\n")
    return buffer.getvalue()


def test_cm_udiff_filename_url_and_raw_path_are_deterministic(tmp_path):
    session_date = date(2025, 10, 31)

    assert cm_udiff_filename(session_date) == (
        "BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv.zip"
    )
    assert cm_udiff_archive_url(session_date).endswith(
        "/BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv.zip"
    )
    assert cm_udiff_raw_path(tmp_path, session_date) == (
        tmp_path
        / "nse"
        / "cm_udiff"
        / "2025"
        / "10"
        / "BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv.zip"
    )


def test_date_from_cm_udiff_filename_requires_canonical_name():
    assert date_from_cm_udiff_filename(
        "BhavCopy_NSE_CM_0_0_0_20260201_F_0000.csv.zip"
    ) == date(2026, 2, 1)
    assert date_from_cm_udiff_filename("cm20260201bhav.csv.zip") is None


def test_load_session_calendar_normalizes_and_sorts_rows(tmp_path):
    source = tmp_path / "sessions.csv"
    write_calendar(
        source,
        [
            ("2026-02-01", "special", "Budget Sunday"),
            ("2025-10-31", "normal", "NSE holiday API"),
        ],
    )

    sessions = load_session_calendar(source)

    assert sessions == (
        TradingSession(date(2025, 10, 31), "NORMAL", "NSE holiday API"),
        TradingSession(date(2026, 2, 1), "SPECIAL", "Budget Sunday"),
    )


def test_load_session_calendar_rejects_duplicates(tmp_path):
    source = tmp_path / "sessions.csv"
    write_calendar(
        source,
        [
            ("2025-10-31", "NORMAL", "NSE holiday API"),
            ("2025-10-31", "SPECIAL", "duplicate"),
        ],
    )

    with pytest.raises(TradingCalendarError, match="duplicate session"):
        load_session_calendar(source)


def test_committed_v0_calendar_contains_expected_special_sessions():
    sessions = load_session_calendar(CALENDAR_PATH)
    by_date = {session.session_date: session for session in sessions}

    assert len(sessions) == 247
    assert by_date[date(2025, 10, 21)].session_type == "SPECIAL"
    assert by_date[date(2026, 2, 1)].session_type == "SPECIAL"
    assert date(2025, 10, 22) not in by_date


def test_audit_cm_udiff_raw_files_reports_missing_and_unexpected(tmp_path):
    sessions = (
        TradingSession(date(2025, 10, 31), "NORMAL", "NSE holiday API"),
        TradingSession(date(2025, 11, 3), "NORMAL", "NSE holiday API"),
    )
    expected = cm_udiff_raw_path(tmp_path, date(2025, 10, 31))
    unexpected = cm_udiff_raw_path(tmp_path, date(2025, 11, 4))
    expected.parent.mkdir(parents=True)
    expected.write_bytes(zip_bytes())
    unexpected.parent.mkdir(parents=True, exist_ok=True)
    unexpected.write_bytes(zip_bytes())

    audit = audit_cm_udiff_raw_files(tmp_path, sessions)

    assert audit.expected_files == (
        expected,
        cm_udiff_raw_path(tmp_path, date(2025, 11, 3)),
    )
    assert audit.missing_files == (cm_udiff_raw_path(tmp_path, date(2025, 11, 3)),)
    assert audit.unexpected_files == (unexpected,)


def test_download_cm_udiff_file_uses_injected_fetcher_and_canonical_path(tmp_path):
    called_urls = []

    def fetch(url):
        called_urls.append(url)
        return zip_bytes()

    path = download_cm_udiff_file(date(2025, 10, 31), tmp_path, fetch_bytes=fetch)

    assert path == cm_udiff_raw_path(tmp_path, date(2025, 10, 31))
    assert path.read_bytes().startswith(b"PK")
    assert called_urls == [cm_udiff_archive_url(date(2025, 10, 31))]


def test_download_cm_udiff_file_does_not_overwrite_by_default(tmp_path):
    path = cm_udiff_raw_path(tmp_path, date(2025, 10, 31))
    path.parent.mkdir(parents=True)
    path.write_bytes(b"existing")

    result = download_cm_udiff_file(
        date(2025, 10, 31),
        tmp_path,
        fetch_bytes=lambda url: pytest.fail("fetch should not be called"),
    )

    assert result == path
    assert path.read_bytes() == b"existing"


def test_download_cm_udiff_file_rejects_non_zip_content(tmp_path):
    with pytest.raises(UDiffAcquisitionError, match="not a ZIP"):
        download_cm_udiff_file(
            date(2025, 10, 31),
            tmp_path,
            fetch_bytes=lambda url: b"not a zip",
        )
