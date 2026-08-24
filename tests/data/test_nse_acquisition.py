from datetime import date
from http.client import RemoteDisconnected
from pathlib import Path
import zipfile

import pytest

from nse_quant.data.nse_acquisition import (
    TradingCalendarError,
    TradingSession,
    UDiffArchiveNotFoundError,
    UDiffAcquisitionError,
    UDiffDownloadRetryableError,
    audit_cm_udiff_raw_files,
    cm_udiff_archive_url,
    cm_udiff_filename,
    cm_udiff_raw_path,
    date_from_cm_udiff_filename,
    download_cm_udiff_file,
    load_session_calendar,
    research_sessions,
)
from nse_quant.data import nse_acquisition


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CALENDAR_PATH = (
    PROJECT_ROOT
    / "data"
    / "calendars"
    / "nse_cm_sessions_2025-08-20_2026-08-19.csv"
)
FULL_WINDOW_CALENDAR_PATH = (
    PROJECT_ROOT
    / "data"
    / "calendars"
    / "nse_cm_sessions_2016-01-01_2026-08-19.csv"
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


def zip_bytes_with_members(*names):
    import io

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name in names:
            archive.writestr(name, "TradDt\n2025-10-31\n")
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


def test_load_session_calendar_accepts_compact_rows(tmp_path):
    source = tmp_path / "sessions.csv"
    source.write_text(
        "date,session_type\n"
        "2026-02-01,S\n"
        "2025-10-31,N\n",
        encoding="utf-8",
    )

    sessions = load_session_calendar(source)

    assert sessions == (
        TradingSession(date(2025, 10, 31), "NORMAL", "COMPACT_CALENDAR"),
        TradingSession(date(2026, 2, 1), "SPECIAL", "COMPACT_CALENDAR"),
    )


def test_load_session_calendar_expands_compact_directives(tmp_path):
    source = tmp_path / "sessions.csv"
    source.write_text(
        "date,session_type\n"
        "2026-01-01,START\n"
        "2026-01-04,S\n"
        "2026-01-05,H\n"
        "2026-01-07,END\n",
        encoding="utf-8",
    )

    sessions = load_session_calendar(source)

    assert sessions == (
        TradingSession(date(2026, 1, 1), "NORMAL", "COMPACT_CALENDAR"),
        TradingSession(date(2026, 1, 2), "NORMAL", "COMPACT_CALENDAR"),
        TradingSession(date(2026, 1, 4), "SPECIAL", "COMPACT_CALENDAR"),
        TradingSession(date(2026, 1, 6), "NORMAL", "COMPACT_CALENDAR"),
        TradingSession(date(2026, 1, 7), "NORMAL", "COMPACT_CALENDAR"),
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


def test_research_sessions_excludes_special_sessions_by_default():
    sessions = (
        TradingSession(date(2025, 10, 20), "NORMAL", "NSE holiday API"),
        TradingSession(date(2025, 10, 21), "SPECIAL", "Muhurat"),
        TradingSession(date(2025, 10, 23), "NORMAL", "NSE holiday API"),
    )

    assert research_sessions(sessions) == (sessions[0], sessions[2])
    assert research_sessions(sessions, include_special=True) == sessions


def test_committed_v0_calendar_contains_expected_special_sessions():
    sessions = load_session_calendar(CALENDAR_PATH)
    by_date = {session.session_date: session for session in sessions}

    assert len(sessions) == 247
    assert by_date[date(2025, 10, 21)].session_type == "SPECIAL"
    assert by_date[date(2026, 2, 1)].session_type == "SPECIAL"
    assert date(2025, 10, 22) not in by_date


def test_committed_full_window_calendar_contains_expected_special_sessions():
    sessions = load_session_calendar(FULL_WINDOW_CALENDAR_PATH)
    by_date = {session.session_date: session for session in sessions}
    special_dates = {
        session.session_date
        for session in sessions
        if session.session_type == "SPECIAL"
    }

    assert len(sessions) == 2631
    assert special_dates == {
        date(2016, 10, 30),
        date(2017, 10, 19),
        date(2018, 11, 7),
        date(2019, 10, 27),
        date(2020, 2, 1),
        date(2020, 11, 14),
        date(2021, 11, 4),
        date(2022, 10, 24),
        date(2023, 11, 12),
        date(2024, 11, 1),
        date(2025, 2, 1),
        date(2025, 10, 21),
        date(2026, 2, 1),
    }
    assert by_date[date(2016, 1, 1)].session_type == "NORMAL"
    assert by_date[date(2026, 8, 19)].session_type == "NORMAL"
    assert date(2024, 7, 6) not in by_date
    assert date(2024, 7, 7) not in by_date
    assert len(research_sessions(sessions)) == 2618


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


def test_download_cm_udiff_file_reuses_valid_existing_archive(tmp_path):
    path = cm_udiff_raw_path(tmp_path, date(2025, 10, 31))
    path.parent.mkdir(parents=True)
    content = zip_bytes()
    path.write_bytes(content)

    result = download_cm_udiff_file(
        date(2025, 10, 31),
        tmp_path,
        fetch_bytes=lambda url: pytest.fail("fetch should not be called"),
    )

    assert result == path
    assert path.read_bytes() == content


def test_download_cm_udiff_file_validates_existing_archive_before_reuse(tmp_path):
    path = cm_udiff_raw_path(tmp_path, date(2025, 10, 31))
    path.parent.mkdir(parents=True)
    path.write_bytes(b"partial interrupted download")

    with pytest.raises(UDiffAcquisitionError, match="not a ZIP"):
        download_cm_udiff_file(
            date(2025, 10, 31),
            tmp_path,
            fetch_bytes=lambda url: pytest.fail("fetch should not be called"),
        )


def test_download_cm_udiff_file_rejects_non_zip_content(tmp_path):
    with pytest.raises(UDiffAcquisitionError, match="not a ZIP"):
        download_cm_udiff_file(
            date(2025, 10, 31),
            tmp_path,
            fetch_bytes=lambda url: b"not a zip",
        )


def test_download_cm_udiff_file_rejects_zip_without_one_csv(tmp_path):
    with pytest.raises(UDiffAcquisitionError, match="exactly one CSV"):
        download_cm_udiff_file(
            date(2025, 10, 31),
            tmp_path,
            fetch_bytes=lambda url: zip_bytes_with_members("one.csv", "two.csv"),
        )


def test_download_cm_udiff_file_retries_transient_errors(tmp_path):
    attempts = []

    def fetch(url):
        attempts.append(url)
        if len(attempts) < 3:
            raise UDiffDownloadRetryableError("temporary")
        return zip_bytes()

    path = download_cm_udiff_file(
        date(2025, 10, 31),
        tmp_path,
        fetch_bytes=fetch,
        max_retries=2,
        retry_delay_seconds=0,
    )

    assert path.exists()
    assert len(attempts) == 3


def test_download_cm_udiff_file_retries_timeout_errors(tmp_path):
    attempts = []

    def fetch(url):
        attempts.append(url)
        if len(attempts) < 2:
            raise TimeoutError("read operation timed out")
        return zip_bytes()

    path = download_cm_udiff_file(
        date(2025, 10, 31),
        tmp_path,
        fetch_bytes=fetch,
        max_retries=1,
        retry_delay_seconds=0,
    )

    assert path.exists()
    assert len(attempts) == 2


def test_download_cm_udiff_file_wraps_exhausted_timeout(tmp_path):
    with pytest.raises(UDiffDownloadRetryableError, match="timed out downloading"):
        download_cm_udiff_file(
            date(2025, 10, 31),
            tmp_path,
            fetch_bytes=lambda url: (_ for _ in ()).throw(
                TimeoutError("read operation timed out")
            ),
            max_retries=0,
            retry_delay_seconds=0,
        )


def test_download_cm_udiff_file_retries_remote_disconnect(tmp_path):
    attempts = []

    def fetch(url):
        attempts.append(url)
        if len(attempts) < 2:
            raise RemoteDisconnected("remote end closed connection without response")
        return zip_bytes()

    path = download_cm_udiff_file(
        date(2025, 10, 31),
        tmp_path,
        fetch_bytes=fetch,
        max_retries=1,
        retry_delay_seconds=0,
    )

    assert path.exists()
    assert len(attempts) == 2


def test_download_cm_udiff_file_wraps_exhausted_remote_disconnect(tmp_path):
    with pytest.raises(
        UDiffDownloadRetryableError,
        match="interrupted HTTP response",
    ):
        download_cm_udiff_file(
            date(2025, 10, 31),
            tmp_path,
            fetch_bytes=lambda url: (_ for _ in ()).throw(
                RemoteDisconnected("remote end closed connection without response")
            ),
            max_retries=0,
            retry_delay_seconds=0,
        )


def test_download_cm_udiff_file_does_not_retry_archive_not_found(tmp_path):
    attempts = []

    def fetch(url):
        attempts.append(url)
        raise UDiffArchiveNotFoundError("not found")

    with pytest.raises(UDiffArchiveNotFoundError):
        download_cm_udiff_file(
            date(2025, 10, 31),
            tmp_path,
            fetch_bytes=fetch,
            max_retries=3,
            retry_delay_seconds=0,
        )

    assert len(attempts) == 1


def test_cm_udiff_fetch_uses_browser_style_headers(monkeypatch):
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"content"

    def fake_urlopen(request, timeout):
        captured["headers"] = dict(request.header_items())
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(nse_acquisition, "urlopen", fake_urlopen)

    assert nse_acquisition._fetch_url("https://example.test/archive.zip") == b"content"

    headers = captured["headers"]
    assert "Windows NT 10.0" in headers["User-agent"]
    assert "Chrome/" in headers["User-agent"]
    assert headers["Referer"] == "https://www.nseindia.com/all-reports"
    assert captured["timeout"] == 60
