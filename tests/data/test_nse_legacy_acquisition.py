from datetime import date
from http.client import RemoteDisconnected
import zipfile

import pytest

from nse_quant.data.nse_legacy_acquisition import (
    LegacyBhavcopyAcquisitionError,
    LegacyBhavcopyArchiveNotFoundError,
    LegacyBhavcopyDownloadRetryableError,
    cm_bhavcopy_archive_url,
    cm_bhavcopy_filename,
    cm_bhavcopy_raw_path,
    date_from_cm_bhavcopy_filename,
    download_cm_bhavcopy_file,
)


def zip_bytes():
    import io

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("cm04JAN2016bhav.csv", "SYMBOL,SERIES\nABC,EQ\n")
    return buffer.getvalue()


def zip_bytes_with_members(*names):
    import io

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name in names:
            archive.writestr(name, "SYMBOL,SERIES\nABC,EQ\n")
    return buffer.getvalue()


def test_cm_bhavcopy_filename_url_and_raw_path_are_deterministic(tmp_path):
    session_date = date(2016, 1, 4)

    assert cm_bhavcopy_filename(session_date) == "cm04JAN2016bhav.csv.zip"
    assert cm_bhavcopy_archive_url(session_date) == (
        "https://nsearchives.nseindia.com/content/historical/EQUITIES/"
        "2016/JAN/cm04JAN2016bhav.csv.zip"
    )
    assert cm_bhavcopy_raw_path(tmp_path, session_date) == (
        tmp_path
        / "nse"
        / "cm_bhavcopy"
        / "2016"
        / "01"
        / "cm04JAN2016bhav.csv.zip"
    )


def test_date_from_cm_bhavcopy_filename_requires_canonical_archive_name():
    assert date_from_cm_bhavcopy_filename("cm05JUL2024bhav.csv.zip") == date(
        2024, 7, 5
    )
    assert date_from_cm_bhavcopy_filename("cm05JUL2024bhav.csv") is None
    assert date_from_cm_bhavcopy_filename("cm32JAN2024bhav.csv.zip") is None
    assert date_from_cm_bhavcopy_filename("BhavCopy_NSE_CM_0_0_0_20240705.zip") is None


def test_download_cm_bhavcopy_file_uses_injected_fetcher_and_canonical_path(tmp_path):
    called_urls = []

    def fetch(url):
        called_urls.append(url)
        return zip_bytes()

    path = download_cm_bhavcopy_file(date(2016, 1, 4), tmp_path, fetch_bytes=fetch)

    assert path == cm_bhavcopy_raw_path(tmp_path, date(2016, 1, 4))
    assert path.read_bytes().startswith(b"PK")
    assert called_urls == [cm_bhavcopy_archive_url(date(2016, 1, 4))]


def test_download_cm_bhavcopy_file_reuses_valid_existing_archive(tmp_path):
    path = cm_bhavcopy_raw_path(tmp_path, date(2016, 1, 4))
    path.parent.mkdir(parents=True)
    content = zip_bytes()
    path.write_bytes(content)

    result = download_cm_bhavcopy_file(
        date(2016, 1, 4),
        tmp_path,
        fetch_bytes=lambda url: pytest.fail("fetch should not be called"),
    )

    assert result == path
    assert path.read_bytes() == content


def test_download_cm_bhavcopy_file_validates_existing_archive_before_reuse(tmp_path):
    path = cm_bhavcopy_raw_path(tmp_path, date(2016, 1, 4))
    path.parent.mkdir(parents=True)
    path.write_bytes(b"partial interrupted download")

    with pytest.raises(LegacyBhavcopyAcquisitionError, match="not a ZIP"):
        download_cm_bhavcopy_file(
            date(2016, 1, 4),
            tmp_path,
            fetch_bytes=lambda url: pytest.fail("fetch should not be called"),
        )


def test_download_cm_bhavcopy_file_rejects_non_zip_content(tmp_path):
    with pytest.raises(LegacyBhavcopyAcquisitionError, match="not a ZIP"):
        download_cm_bhavcopy_file(
            date(2016, 1, 4),
            tmp_path,
            fetch_bytes=lambda url: b"not a zip",
        )


def test_download_cm_bhavcopy_file_rejects_zip_without_one_csv(tmp_path):
    with pytest.raises(LegacyBhavcopyAcquisitionError, match="exactly one CSV"):
        download_cm_bhavcopy_file(
            date(2016, 1, 4),
            tmp_path,
            fetch_bytes=lambda url: zip_bytes_with_members("one.csv", "two.csv"),
        )


def test_download_cm_bhavcopy_file_retries_transient_errors(tmp_path):
    attempts = []

    def fetch(url):
        attempts.append(url)
        if len(attempts) < 3:
            raise LegacyBhavcopyDownloadRetryableError("temporary")
        return zip_bytes()

    path = download_cm_bhavcopy_file(
        date(2016, 1, 4),
        tmp_path,
        fetch_bytes=fetch,
        max_retries=2,
        retry_delay_seconds=0,
    )

    assert path.exists()
    assert len(attempts) == 3


def test_download_cm_bhavcopy_file_retries_timeout_errors(tmp_path):
    attempts = []

    def fetch(url):
        attempts.append(url)
        if len(attempts) < 2:
            raise TimeoutError("read operation timed out")
        return zip_bytes()

    path = download_cm_bhavcopy_file(
        date(2016, 1, 4),
        tmp_path,
        fetch_bytes=fetch,
        max_retries=1,
        retry_delay_seconds=0,
    )

    assert path.exists()
    assert len(attempts) == 2


def test_download_cm_bhavcopy_file_wraps_exhausted_timeout(tmp_path):
    with pytest.raises(
        LegacyBhavcopyDownloadRetryableError,
        match="timed out downloading",
    ):
        download_cm_bhavcopy_file(
            date(2016, 1, 4),
            tmp_path,
            fetch_bytes=lambda url: (_ for _ in ()).throw(
                TimeoutError("read operation timed out")
            ),
            max_retries=0,
            retry_delay_seconds=0,
        )


def test_download_cm_bhavcopy_file_retries_remote_disconnect(tmp_path):
    attempts = []

    def fetch(url):
        attempts.append(url)
        if len(attempts) < 2:
            raise RemoteDisconnected("remote end closed connection without response")
        return zip_bytes()

    path = download_cm_bhavcopy_file(
        date(2016, 1, 4),
        tmp_path,
        fetch_bytes=fetch,
        max_retries=1,
        retry_delay_seconds=0,
    )

    assert path.exists()
    assert len(attempts) == 2


def test_download_cm_bhavcopy_file_wraps_exhausted_remote_disconnect(tmp_path):
    with pytest.raises(
        LegacyBhavcopyDownloadRetryableError,
        match="interrupted HTTP response",
    ):
        download_cm_bhavcopy_file(
            date(2016, 1, 4),
            tmp_path,
            fetch_bytes=lambda url: (_ for _ in ()).throw(
                RemoteDisconnected("remote end closed connection without response")
            ),
            max_retries=0,
            retry_delay_seconds=0,
        )


def test_download_cm_bhavcopy_file_does_not_retry_archive_not_found(tmp_path):
    attempts = []

    def fetch(url):
        attempts.append(url)
        raise LegacyBhavcopyArchiveNotFoundError("not found")

    with pytest.raises(LegacyBhavcopyArchiveNotFoundError):
        download_cm_bhavcopy_file(
            date(2016, 1, 4),
            tmp_path,
            fetch_bytes=fetch,
            max_retries=3,
            retry_delay_seconds=0,
        )

    assert len(attempts) == 1
