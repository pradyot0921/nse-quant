from datetime import date
from decimal import Decimal
import json

import pytest

from nse_quant.data.benchmark import (
    BenchmarkDataError,
    NIFTY100_TRI_NAME,
    fetch_nifty_tri_response,
    parse_nifty_tri_response,
    validate_benchmark_sessions,
    write_benchmark_validation_report,
    write_tri_benchmark_csv,
)
from nse_quant.data.nse_acquisition import TradingSession


def response(rows):
    return json.dumps({"d": json.dumps(rows)}).encode("utf-8")


def row(**overrides):
    values = {
        "Index Name": "Nifty 100",
        "Date": "04 Jan 2016",
        "TotalReturnsIndex": "1000.50",
        "NTR_Value": "990.25",
    }
    values.update(overrides)
    return values


def session(session_date, session_type="NORMAL"):
    return TradingSession(session_date, session_type, "test")


def test_parse_nifty_tri_response_decodes_double_json_and_sorts_ascending():
    bars = parse_nifty_tri_response(
        response(
            [
                row(Date="05 Jan 2016", TotalReturnsIndex="1001.00"),
                row(Date="04 Jan 2016", TotalReturnsIndex="1000.50"),
            ]
        )
    )

    assert [bar.trade_date for bar in bars] == [date(2016, 1, 4), date(2016, 1, 5)]
    assert bars[0].index_name == NIFTY100_TRI_NAME
    assert bars[0].total_return_index == Decimal("1000.50")
    assert bars[0].net_total_return_index == Decimal("990.25")


def test_parse_nifty_tri_response_rejects_html_or_empty_payload():
    with pytest.raises(BenchmarkDataError, match="not JSON"):
        parse_nifty_tri_response("<html></html>")

    with pytest.raises(BenchmarkDataError, match="empty"):
        parse_nifty_tri_response(response([]))


def test_parse_nifty_tri_response_rejects_wrong_index_duplicate_or_non_positive_value():
    with pytest.raises(BenchmarkDataError, match="unexpected TRI index name"):
        parse_nifty_tri_response(response([row(**{"Index Name": "Nifty 50"})]))

    with pytest.raises(BenchmarkDataError, match="duplicate"):
        parse_nifty_tri_response(response([row(), row()]))

    with pytest.raises(BenchmarkDataError, match="must be positive"):
        parse_nifty_tri_response(response([row(TotalReturnsIndex="0")]))


def test_fetch_nifty_tri_response_uses_official_endpoint_payload_and_headers():
    captured = {}

    def fetcher(url, body, headers):
        captured["url"] = url
        captured["body"] = json.loads(body.decode("utf-8"))
        captured["headers"] = headers
        return response([row()])

    raw = fetch_nifty_tri_response(
        index_name="NIFTY 100",
        start_date=date(2016, 1, 1),
        end_date=date(2026, 8, 19),
        fetch_bytes=fetcher,
    )

    assert parse_nifty_tri_response(raw)[0].trade_date == date(2016, 1, 4)
    assert "getTotalReturnIndexString" in captured["url"]
    assert "'name':'NIFTY 100'" in captured["body"]["cinfo"]
    assert "'startDate':'01-Jan-2016'" in captured["body"]["cinfo"]
    assert captured["headers"]["X-Requested-With"] == "XMLHttpRequest"


def test_validate_benchmark_sessions_reports_missing_and_extra_dates():
    bars = parse_nifty_tri_response(
        response(
            [
                row(Date="04 Jan 2016"),
                row(Date="06 Jan 2016", TotalReturnsIndex="1002.00"),
            ]
        )
    )

    report = validate_benchmark_sessions(
        bars,
        (
            session(date(2016, 1, 4)),
            session(date(2016, 1, 5)),
            session(date(2016, 1, 6), "SPECIAL"),
        ),
    )

    assert report.missing_dates == (date(2016, 1, 5),)
    assert report.extra_dates == (date(2016, 1, 6),)
    assert report.has_blocking_problems


def test_write_tri_benchmark_csv_and_report(tmp_path):
    bars = parse_nifty_tri_response(response([row()]))
    csv_output = write_tri_benchmark_csv(bars, tmp_path / "benchmark.csv")
    report = validate_benchmark_sessions(bars, (session(date(2016, 1, 4)),))
    report_output = write_benchmark_validation_report(report, tmp_path / "report.md")

    assert "total_return_index" in csv_output.read_text(encoding="utf-8")
    text = report_output.read_text(encoding="utf-8")
    assert "| Benchmark rows | 1 |" in text
    assert "Total returns Index Values" in text
