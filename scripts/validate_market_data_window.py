from __future__ import annotations

from datetime import date
from pathlib import Path
import argparse

from nse_quant.data.nse_acquisition import load_session_calendar
from nse_quant.data.validation import (
    validate_market_data_files,
    write_market_data_validation_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CALENDAR = PROJECT_ROOT / "data" / "calendars" / "nse_cm_sessions_2016-01-01_2026-08-19.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "validation" / "MARKET_DATA_VALIDATION_V0.md"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", default="data/raw")
    parser.add_argument("--calendar", default=str(DEFAULT_CALENDAR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--include-special", action="store_true")
    parser.add_argument("--fail-on-problems", action="store_true")
    args = parser.parse_args()

    start = date.fromisoformat(args.start) if args.start else None
    end = date.fromisoformat(args.end) if args.end else None
    sessions = tuple(
        session
        for session in load_session_calendar(args.calendar)
        if (start is None or session.session_date >= start)
        and (end is None or session.session_date <= end)
    )

    raw_root = PROJECT_ROOT / args.raw_root
    report = validate_market_data_files(
        raw_root,
        sessions,
        include_special=args.include_special,
    )
    output = write_market_data_validation_report(
        report,
        args.output,
        raw_root=raw_root,
    )

    print(f"Wrote {output}")
    print(f"canonical_bars={len(report.bars)}")
    print(f"missing_files={len(report.missing_files)}")
    print(f"unexpected_files={len(report.unexpected_files)}")
    print(f"file_failures={len(report.file_failures)}")
    print(f"rejected_rows={len(report.rejected_rows)}")

    if args.fail_on_problems and report.has_blocking_problems:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
