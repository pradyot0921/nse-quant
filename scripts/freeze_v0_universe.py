from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from statistics import median
from urllib.request import Request, urlopen
import argparse
import csv
import json

from nse_quant.data.corporate_actions import (
    CorporateActionRecord,
    CorporateActionType,
    ParsedCorporateAction,
    parse_corporate_action,
)
from nse_quant.data.market_data_bars import CanonicalEquityBar
from nse_quant.data.nse_acquisition import load_session_calendar, research_sessions
from nse_quant.data.validation import validate_market_data_files


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CALENDAR = (
    PROJECT_ROOT / "data" / "calendars" / "nse_cm_sessions_2016-01-01_2026-08-19.csv"
)
DEFAULT_RAW_ROOT = PROJECT_ROOT / "data" / "raw"
DEFAULT_CA_ROWS = PROJECT_ROOT / "work" / "corporate_actions_full_window_rows.json"
DEFAULT_CONSTITUENTS_OUTPUT = (
    PROJECT_ROOT / "universes" / "sources" / "nifty100_constituents_2026-08-24.csv"
)
DEFAULT_UNIVERSE_OUTPUT = PROJECT_ROOT / "universes" / "nifty100_v0_20.csv"
DEFAULT_REPORT_OUTPUT = (
    PROJECT_ROOT / "docs" / "validation" / "NIFTY100_V0_UNIVERSE_FREEZE.md"
)
NIFTY100_URL = "https://www.niftyindices.com/IndexConstituent/ind_nifty100list.csv"
FREEZE_DATE = date(2026, 8, 24)
RESEARCH_START = date(2016, 1, 1)
RESEARCH_END = date(2022, 12, 31)
VALIDATION_START = date(2023, 1, 1)
VALIDATION_END = date(2026, 8, 19)
FIRST_BAR_CUTOFF = date(2016, 1, 29)
FINAL_BAR_DATE = date(2026, 8, 19)
MIN_COVERAGE = Decimal("0.98")
MAX_CONSECUTIVE_MISSING = 5
MIN_MEDIAN_TRADED_VALUE = Decimal("250000000")
SELECTION_RULE_VERSION = "nifty100_v0_20_d037"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class Candidate:
    symbol: str
    company_name: str
    industry: str
    series: str
    isin: str


@dataclass(frozen=True)
class CandidateStats:
    symbol: str
    first_bar_date: date | None
    has_final_bar: bool
    research_valid_bars: int
    research_expected_sessions: int
    validation_valid_bars: int
    validation_expected_sessions: int
    full_valid_bars: int
    full_expected_sessions: int
    max_consecutive_missing: int
    median_research_traded_value: Decimal | None

    @property
    def research_coverage(self) -> Decimal:
        return _coverage(self.research_valid_bars, self.research_expected_sessions)

    @property
    def validation_coverage(self) -> Decimal:
        return _coverage(self.validation_valid_bars, self.validation_expected_sessions)


@dataclass(frozen=True)
class Exclusion:
    symbol: str
    reason: str
    detail: str


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", default=str(DEFAULT_RAW_ROOT))
    parser.add_argument("--calendar", default=str(DEFAULT_CALENDAR))
    parser.add_argument("--corporate-actions-json", default=str(DEFAULT_CA_ROWS))
    parser.add_argument("--nifty100-url", default=NIFTY100_URL)
    parser.add_argument("--constituents-output", default=str(DEFAULT_CONSTITUENTS_OUTPUT))
    parser.add_argument("--universe-output", default=str(DEFAULT_UNIVERSE_OUTPUT))
    parser.add_argument("--report-output", default=str(DEFAULT_REPORT_OUTPUT))
    args = parser.parse_args()

    constituents_csv = fetch_nifty100_constituents(args.nifty100_url)
    constituents_output = Path(args.constituents_output)
    constituents_output.parent.mkdir(parents=True, exist_ok=True)
    constituents_output.write_bytes(constituents_csv)
    candidates = parse_constituents_csv(constituents_csv)

    sessions = tuple(load_session_calendar(args.calendar))
    ordinary_sessions = tuple(research_sessions(sessions))
    validation_report = validate_market_data_files(args.raw_root, sessions)
    if validation_report.has_blocking_problems:
        raise SystemExit("market-data validation has blocking problems; aborting universe freeze")

    bars_by_symbol = _bars_by_symbol(validation_report.bars)
    stats_by_symbol = {
        candidate.symbol: compute_candidate_stats(
            candidate.symbol,
            bars_by_symbol.get(candidate.symbol, ()),
            ordinary_sessions,
        )
        for candidate in candidates
    }
    actions_by_symbol = unsupported_actions_by_symbol(
        Path(args.corporate_actions_json),
        {candidate.symbol for candidate in candidates},
    )

    ranked_candidates, exclusions = select_universe(
        candidates,
        stats_by_symbol,
        actions_by_symbol,
    )
    selected = ranked_candidates[:20]
    if len(selected) < 20:
        raise SystemExit(
            f"only {len(selected)} candidates passed pre-registered filters; "
            "halt and record a new decision before changing thresholds"
        )

    universe_output = Path(args.universe_output)
    universe_output.parent.mkdir(parents=True, exist_ok=True)
    write_universe_csv(universe_output, selected, stats_by_symbol)

    report_output = write_freeze_report(
        Path(args.report_output),
        candidates=candidates,
        ranked_candidates=ranked_candidates,
        selected=selected,
        exclusions=exclusions,
        stats_by_symbol=stats_by_symbol,
        actions_by_symbol=actions_by_symbol,
        constituents_output=constituents_output,
        nifty100_url=args.nifty100_url,
        validation_report_bar_count=len(validation_report.bars),
    )

    print(f"Wrote {constituents_output}")
    print(f"Wrote {universe_output}")
    print(f"Wrote {report_output}")
    print(f"candidates={len(candidates)}")
    print(f"eligible_after_filters={len(ranked_candidates)}")
    print(f"selected={len(selected)}")
    print(f"excluded={len(exclusions)}")
    return 0


def fetch_nifty100_constituents(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/csv,*/*",
        },
    )
    with urlopen(request, timeout=60) as response:
        return response.read()


def parse_constituents_csv(content: bytes) -> tuple[Candidate, ...]:
    text = content.decode("utf-8-sig")
    rows = tuple(csv.DictReader(text.splitlines()))
    candidates = []
    seen = set()
    for row in rows:
        symbol = row["Symbol"].strip().upper()
        if not symbol:
            continue
        if symbol in seen:
            raise ValueError(f"duplicate Nifty 100 symbol {symbol}")
        seen.add(symbol)
        candidates.append(
            Candidate(
                symbol=symbol,
                company_name=row["Company Name"].strip(),
                industry=row.get("Industry", "").strip(),
                series=row.get("Series", "").strip().upper(),
                isin=row.get("ISIN Code", "").strip().upper(),
            )
        )
    if len(candidates) != 100:
        raise ValueError(f"expected 100 Nifty 100 candidates, found {len(candidates)}")
    return tuple(candidates)


def compute_candidate_stats(
    symbol: str,
    bars: tuple[CanonicalEquityBar, ...],
    ordinary_sessions,
) -> CandidateStats:
    by_date = {bar.trade_date: bar for bar in bars if bar.symbol == symbol}
    session_dates = tuple(session.session_date for session in ordinary_sessions)
    research_dates = tuple(
        session_date
        for session_date in session_dates
        if RESEARCH_START <= session_date <= RESEARCH_END
    )
    validation_dates = tuple(
        session_date
        for session_date in session_dates
        if VALIDATION_START <= session_date <= VALIDATION_END
    )
    full_dates = tuple(
        session_date
        for session_date in session_dates
        if RESEARCH_START <= session_date <= VALIDATION_END
    )
    traded_values = [
        by_date[session_date].traded_value
        for session_date in research_dates
        if session_date in by_date and by_date[session_date].traded_value > 0
    ]
    median_traded_value = (
        Decimal(str(median(traded_values))) if traded_values else None
    )
    valid_dates = tuple(sorted(by_date))
    return CandidateStats(
        symbol=symbol,
        first_bar_date=valid_dates[0] if valid_dates else None,
        has_final_bar=FINAL_BAR_DATE in by_date,
        research_valid_bars=sum(1 for session_date in research_dates if session_date in by_date),
        research_expected_sessions=len(research_dates),
        validation_valid_bars=sum(1 for session_date in validation_dates if session_date in by_date),
        validation_expected_sessions=len(validation_dates),
        full_valid_bars=sum(1 for session_date in full_dates if session_date in by_date),
        full_expected_sessions=len(full_dates),
        max_consecutive_missing=max_consecutive_missing(full_dates, set(by_date)),
        median_research_traded_value=median_traded_value,
    )


def unsupported_actions_by_symbol(
    corporate_actions_json: Path,
    symbols: set[str],
) -> dict[str, tuple[ParsedCorporateAction, ...]]:
    rows = json.loads(corporate_actions_json.read_text(encoding="utf-8"))
    unsupported: dict[str, list[ParsedCorporateAction]] = defaultdict(list)
    for row in rows:
        symbol = str(row.get("symbol", "")).strip().upper()
        series = str(row.get("series", "")).strip().upper()
        if symbol not in symbols or series != "EQ":
            continue
        record = CorporateActionRecord(
            symbol=symbol,
            purpose=str(row.get("subject", "")).strip(),
            ex_date=_parse_nse_date(str(row.get("exDate", "")).strip()),
            record_date=_optional_nse_date(str(row.get("recDate", "")).strip()),
        )
        if not (RESEARCH_START <= record.ex_date <= VALIDATION_END):
            continue
        action = parse_corporate_action(record)
        if action.action_type == CorporateActionType.UNSUPPORTED:
            unsupported[symbol].append(action)
    return {symbol: tuple(actions) for symbol, actions in unsupported.items()}


def select_universe(
    candidates: tuple[Candidate, ...],
    stats_by_symbol: dict[str, CandidateStats],
    actions_by_symbol: dict[str, tuple[ParsedCorporateAction, ...]],
) -> tuple[tuple[Candidate, ...], tuple[Exclusion, ...]]:
    exclusions: list[Exclusion] = []
    survivors = list(candidates)

    survivors = _filter(
        survivors,
        exclusions,
        lambda candidate: candidate.series == "EQ",
        "non_eq_candidate_series",
        lambda candidate: f"candidate source series={candidate.series or '(blank)'}",
    )
    survivors = _filter(
        survivors,
        exclusions,
        lambda candidate: candidate.symbol not in actions_by_symbol,
        "unsupported_corporate_action",
        lambda candidate: _unsupported_detail(actions_by_symbol[candidate.symbol]),
    )
    survivors = _filter(
        survivors,
        exclusions,
        lambda candidate: (
            stats_by_symbol[candidate.symbol].first_bar_date is not None
            and stats_by_symbol[candidate.symbol].first_bar_date <= FIRST_BAR_CUTOFF
        ),
        "insufficient_start_history",
        lambda candidate: f"first_bar_date={stats_by_symbol[candidate.symbol].first_bar_date}",
    )
    survivors = _filter(
        survivors,
        exclusions,
        lambda candidate: stats_by_symbol[candidate.symbol].has_final_bar,
        "missing_final_bar",
        lambda candidate: f"no valid bar on {FINAL_BAR_DATE}",
    )
    survivors = _filter(
        survivors,
        exclusions,
        lambda candidate: (
            stats_by_symbol[candidate.symbol].research_coverage >= MIN_COVERAGE
            and stats_by_symbol[candidate.symbol].validation_coverage >= MIN_COVERAGE
        ),
        "coverage_below_threshold",
        lambda candidate: (
            f"research={_pct(stats_by_symbol[candidate.symbol].research_coverage)}; "
            f"validation={_pct(stats_by_symbol[candidate.symbol].validation_coverage)}"
        ),
    )
    survivors = _filter(
        survivors,
        exclusions,
        lambda candidate: (
            stats_by_symbol[candidate.symbol].max_consecutive_missing
            <= MAX_CONSECUTIVE_MISSING
        ),
        "missing_run_above_threshold",
        lambda candidate: (
            f"max_consecutive_missing="
            f"{stats_by_symbol[candidate.symbol].max_consecutive_missing}"
        ),
    )
    survivors = _filter(
        survivors,
        exclusions,
        lambda candidate: (
            stats_by_symbol[candidate.symbol].median_research_traded_value is not None
            and stats_by_symbol[candidate.symbol].median_research_traded_value
            >= MIN_MEDIAN_TRADED_VALUE
        ),
        "liquidity_below_threshold",
        lambda candidate: (
            f"median_research_traded_value="
            f"{stats_by_symbol[candidate.symbol].median_research_traded_value}"
        ),
    )

    ranked = tuple(
        sorted(
            survivors,
            key=lambda candidate: (
                -stats_by_symbol[candidate.symbol].median_research_traded_value,
                -stats_by_symbol[candidate.symbol].research_valid_bars,
                candidate.symbol,
            ),
        )
    )
    return ranked, tuple(exclusions)


def write_universe_csv(
    output: Path,
    selected: tuple[Candidate, ...],
    stats_by_symbol: dict[str, CandidateStats],
) -> None:
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "symbol",
                "company_name",
                "industry",
                "selection_date",
                "selection_rule_version",
                "median_daily_raw_traded_value_inr",
                "research_valid_bar_coverage",
                "validation_valid_bar_coverage",
                "full_max_consecutive_missing_sessions",
                "notes",
            ]
        )
        for candidate in selected:
            stats = stats_by_symbol[candidate.symbol]
            writer.writerow(
                [
                    candidate.symbol,
                    candidate.company_name,
                    candidate.industry,
                    FREEZE_DATE.isoformat(),
                    SELECTION_RULE_VERSION,
                    _money(stats.median_research_traded_value),
                    str(stats.research_coverage),
                    str(stats.validation_coverage),
                    stats.max_consecutive_missing,
                    "mechanically selected by D-037 before B001 execution",
                ]
            )


def write_freeze_report(
    output: Path,
    *,
    candidates: tuple[Candidate, ...],
    ranked_candidates: tuple[Candidate, ...],
    selected: tuple[Candidate, ...],
    exclusions: tuple[Exclusion, ...],
    stats_by_symbol: dict[str, CandidateStats],
    actions_by_symbol: dict[str, tuple[ParsedCorporateAction, ...]],
    constituents_output: Path,
    nifty100_url: str,
    validation_report_bar_count: int,
) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    exclusions_by_reason = CounterDict(exclusions)
    lines = [
        "# Nifty 100 V0 Universe Freeze",
        "",
        f"Freeze date: `{FREEZE_DATE}`",
        f"Candidate source URL: `{nifty100_url}`",
        f"Saved candidate source: `{_slash(constituents_output.relative_to(PROJECT_ROOT))}`",
        f"Selection rule version: `{SELECTION_RULE_VERSION}`",
        "",
        "## Bias Labels",
        "",
        "```text",
        "SURVIVORSHIP-BIASED: YES",
        "POINT-IN-TIME UNIVERSE: NO",
        "UNSUPPORTED-CORPORATE-ACTION FILTER: YES",
        "```",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Candidate count before any filter | {len(candidates)} |",
        f"| Canonical market-data bars available | {validation_report_bar_count} |",
        f"| Symbols with unsupported corporate actions | {len(actions_by_symbol)} |",
        f"| Total exclusions | {len(exclusions)} |",
        f"| Eligible candidates after all filters | {len(ranked_candidates)} |",
        f"| Eligible but not selected | {max(0, len(ranked_candidates) - len(selected))} |",
        f"| Selected symbols | {len(selected)} |",
        "",
        "## Exclusion Counts",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ]
    for reason, count in sorted(exclusions_by_reason.items()):
        lines.append(f"| {reason} | {count} |")

    lines.extend(
        [
            "",
            "## Selected Universe",
            "",
            "| Rank | Symbol | Company | Median Raw Traded Value INR | Research Coverage | Validation Coverage | Max Missing Run |",
            "| ---: | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for rank, candidate in enumerate(selected, start=1):
        stats = stats_by_symbol[candidate.symbol]
        lines.append(
            f"| {rank} | {candidate.symbol} | {_md(candidate.company_name)} | "
            f"{_money(stats.median_research_traded_value)} | "
            f"{_pct(stats.research_coverage)} | {_pct(stats.validation_coverage)} | "
            f"{stats.max_consecutive_missing} |"
        )

    lines.extend(
        [
            "",
            "## Eligible But Not Selected",
            "",
            "| Rank | Symbol | Company | Median Raw Traded Value INR | Research Coverage | Validation Coverage | Max Missing Run |",
            "| ---: | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for rank, candidate in enumerate(ranked_candidates[20:], start=21):
        stats = stats_by_symbol[candidate.symbol]
        lines.append(
            f"| {rank} | {candidate.symbol} | {_md(candidate.company_name)} | "
            f"{_money(stats.median_research_traded_value)} | "
            f"{_pct(stats.research_coverage)} | {_pct(stats.validation_coverage)} | "
            f"{stats.max_consecutive_missing} |"
        )

    lines.extend(
        [
            "",
            "## Excluded Candidates",
            "",
            "| Symbol | Reason | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for exclusion in sorted(exclusions, key=lambda item: (item.reason, item.symbol)):
        lines.append(
            f"| {exclusion.symbol} | {exclusion.reason} | {_md(exclusion.detail)} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This artifact freezes only the V0 universe. No strategy result has been",
            "computed or inspected. Changing the selected symbols or thresholds after",
            "this point requires a new universe version and decision entry.",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def max_consecutive_missing(session_dates: tuple[date, ...], observed_dates: set[date]) -> int:
    longest = 0
    current = 0
    for session_date in session_dates:
        if session_date in observed_dates:
            current = 0
        else:
            current += 1
            longest = max(longest, current)
    return longest


def _filter(
    candidates: list[Candidate],
    exclusions: list[Exclusion],
    predicate,
    reason: str,
    detail,
) -> list[Candidate]:
    survivors = []
    for candidate in candidates:
        if predicate(candidate):
            survivors.append(candidate)
        else:
            exclusions.append(Exclusion(candidate.symbol, reason, detail(candidate)))
    return survivors


def _bars_by_symbol(
    bars: tuple[CanonicalEquityBar, ...],
) -> dict[str, tuple[CanonicalEquityBar, ...]]:
    grouped: dict[str, list[CanonicalEquityBar]] = defaultdict(list)
    for bar in bars:
        grouped[bar.symbol].append(bar)
    return {symbol: tuple(items) for symbol, items in grouped.items()}


def _unsupported_detail(actions: tuple[ParsedCorporateAction, ...]) -> str:
    return "; ".join(
        f"{action.ex_date}: {action.purpose}" for action in sorted(actions, key=lambda item: item.ex_date)
    )


def _parse_nse_date(value: str) -> date:
    from datetime import datetime

    return datetime.strptime(value, "%d-%b-%Y").date()


def _optional_nse_date(value: str) -> date | None:
    if not value or value == "-":
        return None
    return _parse_nse_date(value)


def _coverage(valid: int, expected: int) -> Decimal:
    if expected == 0:
        return Decimal("0")
    return (Decimal(valid) / Decimal(expected)).quantize(Decimal("0.000001"))


def _pct(value: Decimal) -> str:
    return f"{(value * Decimal('100')).quantize(Decimal('0.01'))}%"


def _money(value: Decimal | None) -> str:
    if value is None:
        return ""
    return str(value.quantize(Decimal("0.01")))


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _slash(path: Path) -> str:
    return str(path).replace("\\", "/")


def CounterDict(exclusions: tuple[Exclusion, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for exclusion in exclusions:
        counts[exclusion.reason] = counts.get(exclusion.reason, 0) + 1
    return counts


if __name__ == "__main__":
    raise SystemExit(main())
