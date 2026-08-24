from __future__ import annotations

from datetime import date
from pathlib import Path
import argparse

from nse_quant.data.benchmark import (
    BenchmarkDataError,
    NIFTY100_TRI_NAME,
    fetch_nifty_tri_response,
    parse_nifty_tri_response,
    validate_benchmark_sessions,
    write_benchmark_validation_report,
    write_tri_benchmark_csv,
)
from nse_quant.data.nse_acquisition import load_session_calendar


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CALENDAR = (
    PROJECT_ROOT / "data" / "calendars" / "nse_cm_sessions_2016-01-01_2026-08-19.csv"
)
DEFAULT_RAW_OUTPUT = (
    PROJECT_ROOT / "data" / "raw" / "benchmarks" / "nifty100_tri_2016-01-01_2026-08-19.json"
)
DEFAULT_PROCESSED_OUTPUT = (
    PROJECT_ROOT / "data" / "processed" / "benchmarks" / "nifty100_tri_2016-01-01_2026-08-19.csv"
)
DEFAULT_REPORT_OUTPUT = (
    PROJECT_ROOT / "docs" / "validation" / "NIFTY100_TRI_BENCHMARK_V0.md"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index-name", default=NIFTY100_TRI_NAME)
    parser.add_argument("--start", default="2016-01-01")
    parser.add_argument("--end", default="2026-08-19")
    parser.add_argument("--calendar", default=str(DEFAULT_CALENDAR))
    parser.add_argument("--raw-output", default=str(DEFAULT_RAW_OUTPUT))
    parser.add_argument("--processed-output", default=str(DEFAULT_PROCESSED_OUTPUT))
    parser.add_argument("--report-output", default=str(DEFAULT_REPORT_OUTPUT))
    parser.add_argument("--fail-on-problems", action="store_true")
    args = parser.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    raw = fetch_nifty_tri_response(
        index_name=args.index_name,
        start_date=start,
        end_date=end,
    )
    try:
        bars = parse_nifty_tri_response(raw, expected_index_name=args.index_name)
    except BenchmarkDataError as exc:
        raise SystemExit(
            f"benchmark response is not usable; raw response was not saved: {exc}"
        ) from exc

    raw_output = Path(args.raw_output)
    raw_output.parent.mkdir(parents=True, exist_ok=True)
    raw_output.write_bytes(raw)
    processed_output = write_tri_benchmark_csv(bars, args.processed_output)
    sessions = tuple(
        session
        for session in load_session_calendar(args.calendar)
        if start <= session.session_date <= end
    )
    report = validate_benchmark_sessions(bars, sessions)
    report_output = write_benchmark_validation_report(report, args.report_output)

    print(f"Wrote raw response {raw_output}")
    print(f"Wrote processed benchmark {processed_output}")
    print(f"Wrote {report_output}")
    print(f"benchmark_rows={len(report.bars)}")
    print(f"sessions_checked={len(report.sessions_checked)}")
    print(f"missing_dates={len(report.missing_dates)}")
    print(f"extra_dates={len(report.extra_dates)}")

    if args.fail_on_problems and report.has_blocking_problems:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
