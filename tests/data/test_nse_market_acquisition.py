from datetime import date
import io
import zipfile

import pytest

from nse_quant.data.nse_acquisition import TradingSession, UDiffArchiveNotFoundError
from nse_quant.data.nse_legacy_acquisition import (
    LegacyBhavcopyArchiveNotFoundError,
    cm_bhavcopy_raw_path,
)
from nse_quant.data.nse_market_acquisition import (
    CM_UDIFF,
    LEGACY_CM_BHAVCOPY,
    MarketDataAcquisitionError,
    audit_market_data_raw_files,
    download_market_data_files,
    market_data_raw_path,
    market_data_source_for_session,
)


def zip_bytes(member_name):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(member_name, "sample\n")
    return buffer.getvalue()


def legacy_zip_bytes():
    return zip_bytes("cm04JAN2016bhav.csv")


def udiff_zip_bytes():
    return zip_bytes("BhavCopy_NSE_CM_0_0_0_20240708_F_0000.csv")


def session(session_date):
    return TradingSession(session_date, "NORMAL", "test calendar")


def test_market_data_source_bridge_routes_legacy_and_udiff_dates():
    assert market_data_source_for_session(date(2024, 7, 5)) == LEGACY_CM_BHAVCOPY
    assert market_data_source_for_session(date(2024, 7, 8)) == CM_UDIFF

    with pytest.raises(MarketDataAcquisitionError, match="transition gap"):
        market_data_source_for_session(date(2024, 7, 6))


def test_market_data_raw_path_uses_source_specific_storage(tmp_path):
    assert market_data_raw_path(tmp_path, date(2016, 1, 4)) == (
        tmp_path / "nse" / "cm_bhavcopy" / "2016" / "01" / "cm04JAN2016bhav.csv.zip"
    )
    assert market_data_raw_path(tmp_path, date(2024, 7, 8)) == (
        tmp_path
        / "nse"
        / "cm_udiff"
        / "2024"
        / "07"
        / "BhavCopy_NSE_CM_0_0_0_20240708_F_0000.csv.zip"
    )


def test_download_market_data_files_uses_registered_source_for_each_session(tmp_path):
    legacy_urls = []
    udiff_urls = []

    report = download_market_data_files(
        (session(date(2016, 1, 4)), session(date(2024, 7, 8))),
        tmp_path,
        legacy_fetch_bytes=lambda url: legacy_urls.append(url) or legacy_zip_bytes(),
        udiff_fetch_bytes=lambda url: udiff_urls.append(url) or udiff_zip_bytes(),
        retry_delay_seconds=0,
    )

    assert [(record.session_date, record.source, record.status) for record in report.records] == [
        (date(2016, 1, 4), LEGACY_CM_BHAVCOPY, "downloaded"),
        (date(2024, 7, 8), CM_UDIFF, "downloaded"),
    ]
    assert len(legacy_urls) == 1
    assert len(udiff_urls) == 1
    assert report.missing_archives == ()
    assert report.failed_archives == ()


def test_download_market_data_files_records_404_and_continues(tmp_path):
    report = download_market_data_files(
        (session(date(2016, 1, 4)), session(date(2024, 7, 8))),
        tmp_path,
        legacy_fetch_bytes=lambda url: (_ for _ in ()).throw(
            LegacyBhavcopyArchiveNotFoundError("legacy missing")
        ),
        udiff_fetch_bytes=lambda url: udiff_zip_bytes(),
        retry_delay_seconds=0,
    )

    assert len(report.records) == 1
    assert report.records[0].session_date == date(2024, 7, 8)
    assert len(report.missing_archives) == 1
    assert report.missing_archives[0].session_date == date(2016, 1, 4)
    assert report.failed_archives == ()


def test_download_market_data_files_redownloads_one_corrupt_existing_file(tmp_path):
    path = cm_bhavcopy_raw_path(tmp_path, date(2016, 1, 4))
    path.parent.mkdir(parents=True)
    path.write_bytes(b"interrupted partial file")
    attempts = []

    report = download_market_data_files(
        (session(date(2016, 1, 4)),),
        tmp_path,
        legacy_fetch_bytes=lambda url: attempts.append(url) or legacy_zip_bytes(),
        retry_delay_seconds=0,
    )

    assert len(attempts) == 1
    assert [(record.session_date, record.status) for record in report.records] == [
        (date(2016, 1, 4), "redownloaded")
    ]
    assert path.read_bytes().startswith(b"PK")
    assert report.missing_archives == ()
    assert report.failed_archives == ()


def test_download_market_data_files_reports_failed_redownload(tmp_path):
    path = cm_bhavcopy_raw_path(tmp_path, date(2016, 1, 4))
    path.parent.mkdir(parents=True)
    path.write_bytes(b"interrupted partial file")

    report = download_market_data_files(
        (session(date(2016, 1, 4)),),
        tmp_path,
        legacy_fetch_bytes=lambda url: b"still not a zip",
        retry_delay_seconds=0,
    )

    assert report.records == ()
    assert report.missing_archives == ()
    assert len(report.failed_archives) == 1
    assert report.failed_archives[0].session_date == date(2016, 1, 4)


def test_download_market_data_files_records_udiff_404_after_corrupt_cache_retry(tmp_path):
    path = market_data_raw_path(tmp_path, date(2024, 7, 8))
    path.parent.mkdir(parents=True)
    path.write_bytes(b"interrupted partial file")

    report = download_market_data_files(
        (session(date(2024, 7, 8)),),
        tmp_path,
        udiff_fetch_bytes=lambda url: (_ for _ in ()).throw(
            UDiffArchiveNotFoundError("udiff missing")
        ),
        retry_delay_seconds=0,
    )

    assert report.records == ()
    assert len(report.missing_archives) == 1
    assert report.failed_archives == ()


def test_audit_market_data_raw_files_spans_both_source_families(tmp_path):
    expected_legacy = market_data_raw_path(tmp_path, date(2016, 1, 4))
    unexpected_udiff = market_data_raw_path(tmp_path, date(2024, 7, 9))
    expected_legacy.parent.mkdir(parents=True)
    unexpected_udiff.parent.mkdir(parents=True)
    expected_legacy.write_bytes(legacy_zip_bytes())
    unexpected_udiff.write_bytes(udiff_zip_bytes())

    audit = audit_market_data_raw_files(
        tmp_path,
        (session(date(2016, 1, 4)), session(date(2024, 7, 8))),
    )

    assert audit.expected_files == (
        expected_legacy,
        market_data_raw_path(tmp_path, date(2024, 7, 8)),
    )
    assert audit.missing_files == (market_data_raw_path(tmp_path, date(2024, 7, 8)),)
    assert audit.unexpected_files == (unexpected_udiff,)
