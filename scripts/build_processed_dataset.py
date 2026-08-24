from __future__ import annotations

from pathlib import Path
import argparse

from nse_quant.data.nse_acquisition import load_session_calendar
from nse_quant.data.processed_dataset import (
    build_processed_dataset,
    load_corporate_action_rows,
    load_universe_symbols,
    write_processed_dataset_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CALENDAR = (
    PROJECT_ROOT / "data" / "calendars" / "nse_cm_sessions_2016-01-01_2026-08-19.csv"
)
DEFAULT_RAW_ROOT = PROJECT_ROOT / "data" / "raw"
DEFAULT_UNIVERSE = PROJECT_ROOT / "universes" / "nifty100_v0_20.csv"
DEFAULT_CA_ROWS = PROJECT_ROOT / "work" / "corporate_actions_full_window_rows.json"
DEFAULT_PROCESSED_OUTPUT = (
    PROJECT_ROOT / "data" / "processed" / "nifty100_v0_adjusted_ohlcv.csv"
)
DEFAULT_REPORT_OUTPUT = (
    PROJECT_ROOT / "docs" / "validation" / "PROCESSED_DATASET_V0.md"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", default=str(DEFAULT_RAW_ROOT))
    parser.add_argument("--calendar", default=str(DEFAULT_CALENDAR))
    parser.add_argument("--universe", default=str(DEFAULT_UNIVERSE))
    parser.add_argument("--corporate-actions-json", default=str(DEFAULT_CA_ROWS))
    parser.add_argument("--processed-output", default=str(DEFAULT_PROCESSED_OUTPUT))
    parser.add_argument("--report-output", default=str(DEFAULT_REPORT_OUTPUT))
    args = parser.parse_args()

    sessions = load_session_calendar(args.calendar)
    symbols = load_universe_symbols(args.universe)
    corporate_action_rows = load_corporate_action_rows(args.corporate_actions_json)
    report = build_processed_dataset(
        raw_root=args.raw_root,
        sessions=sessions,
        universe_symbols=symbols,
        corporate_action_rows=corporate_action_rows,
        output_path=args.processed_output,
    )
    report_output = write_processed_dataset_report(
        report,
        args.report_output,
        project_root=PROJECT_ROOT,
    )

    print(f"Wrote {report.output_path}")
    print(f"Wrote {report_output}")
    print(f"dataset_version={report.dataset_version}")
    print(f"symbols={len(report.universe_symbols)}")
    print(f"ordinary_sessions={len(report.ordinary_sessions_checked)}")
    print(f"processed_bars={len(report.bars)}")
    print(f"sha256={report.output_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
