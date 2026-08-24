"""Processed V0 equity dataset construction.

This module combines the already-validated raw market-data archives, the frozen
V0 universe, and parsed corporate actions into one adjusted OHLCV dataset.
Raw market data remains immutable and processed CSV outputs are local artifacts.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
import csv
import json
from typing import Iterable

from nse_quant.data.corporate_actions import (
    AdjustedOHLCVBar,
    CorporateActionRecord,
    CorporateActionType,
    OHLCVBar,
    ParsedCorporateAction,
    UnsupportedCorporateActionError,
    adjust_ohlcv_bars,
    parse_corporate_action,
    validate_actions,
)
from nse_quant.data.market_data_bars import CanonicalEquityBar
from nse_quant.data.nse_acquisition import TradingSession, research_sessions
from nse_quant.data.validation import MarketDataValidationReport, validate_market_data_files


PROCESSED_DATASET_VERSION = "nifty100_v0_adjusted_ohlcv_d039"


class ProcessedDatasetError(RuntimeError):
    """Raised when a processed dataset cannot be built without data loss."""


@dataclass(frozen=True)
class ProcessedEquityBar:
    trade_date: date
    symbol: str
    isin: str | None
    series: str
    source_format: str
    raw_open: Decimal
    raw_high: Decimal
    raw_low: Decimal
    raw_close: Decimal
    raw_volume: Decimal
    raw_traded_value: Decimal
    previous_close: Decimal
    last_price: Decimal
    transaction_count: int
    adjusted_open: Decimal
    adjusted_high: Decimal
    adjusted_low: Decimal
    adjusted_close: Decimal
    adjusted_volume: Decimal
    price_factor: Decimal
    volume_factor: Decimal


@dataclass(frozen=True)
class ProcessedDatasetReport:
    dataset_version: str
    universe_symbols: tuple[str, ...]
    ordinary_sessions_checked: tuple[TradingSession, ...]
    market_validation: MarketDataValidationReport
    corporate_actions: tuple[ParsedCorporateAction, ...]
    bars: tuple[ProcessedEquityBar, ...]
    output_path: Path
    output_sha256: str

    @property
    def has_blocking_problems(self) -> bool:
        return self.market_validation.has_blocking_problems


def build_processed_dataset(
    *,
    raw_root: str | Path,
    sessions: Iterable[TradingSession],
    universe_symbols: Iterable[str],
    corporate_action_rows: Iterable[dict[str, object]],
    output_path: str | Path,
) -> ProcessedDatasetReport:
    """Build the adjusted V0 dataset for the frozen universe."""

    symbols = tuple(_normalise_symbols(universe_symbols))
    if not symbols:
        raise ProcessedDatasetError("universe_symbols is empty")

    session_tuple = tuple(sessions)
    ordinary_sessions = research_sessions(session_tuple)
    market_report = validate_market_data_files(raw_root, session_tuple)
    if market_report.has_blocking_problems:
        raise ProcessedDatasetError(
            "market-data validation has blocking problems; "
            "review missing files, parser failures, or rejected rows first"
        )

    actions = parse_corporate_action_rows(corporate_action_rows, symbols)
    try:
        validate_actions(
            symbols,
            actions,
            start_date=ordinary_sessions[0].session_date if ordinary_sessions else None,
            end_date=ordinary_sessions[-1].session_date if ordinary_sessions else None,
        )
    except UnsupportedCorporateActionError as exc:
        raise ProcessedDatasetError(str(exc)) from exc

    selected_bars = _selected_canonical_bars(market_report.bars, symbols)
    _validate_complete_symbol_sessions(selected_bars, symbols, ordinary_sessions)
    adjusted_bars = adjust_ohlcv_bars(
        (_ohlcv_bar(bar) for bar in selected_bars),
        actions,
    )
    processed_bars = tuple(
        _processed_bar(raw, adjusted)
        for raw, adjusted in zip(selected_bars, adjusted_bars, strict=True)
    )
    output = write_processed_dataset_csv(processed_bars, output_path)
    digest = _sha256_file(output)

    return ProcessedDatasetReport(
        dataset_version=PROCESSED_DATASET_VERSION,
        universe_symbols=symbols,
        ordinary_sessions_checked=ordinary_sessions,
        market_validation=market_report,
        corporate_actions=actions,
        bars=processed_bars,
        output_path=output,
        output_sha256=digest,
    )


def load_universe_symbols(path: str | Path) -> tuple[str, ...]:
    """Load the frozen universe symbols in CSV order."""

    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    return tuple(_normalise_symbols(row["symbol"] for row in rows))


def load_corporate_action_rows(path: str | Path) -> tuple[dict[str, object], ...]:
    """Load raw corporate-action endpoint rows saved by the scan step."""

    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ProcessedDatasetError("corporate-action JSON must contain a list")
    return tuple(row for row in rows if isinstance(row, dict))


def parse_corporate_action_rows(
    rows: Iterable[dict[str, object]],
    symbols: Iterable[str],
) -> tuple[ParsedCorporateAction, ...]:
    """Parse EQ corporate-action rows for selected symbols only."""

    symbol_set = set(_normalise_symbols(symbols))
    actions = []
    for row in rows:
        symbol = str(row.get("symbol", "")).strip().upper()
        series = str(row.get("series", "")).strip().upper()
        if symbol not in symbol_set or series != "EQ":
            continue
        actions.append(parse_corporate_action(_corporate_action_record(row)))
    return tuple(sorted(actions, key=lambda action: (action.symbol, action.ex_date, action.purpose)))


def write_processed_dataset_csv(
    bars: Iterable[ProcessedEquityBar],
    output_path: str | Path,
) -> Path:
    """Write processed bars to a deterministic CSV."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "trade_date",
        "symbol",
        "isin",
        "series",
        "source_format",
        "raw_open",
        "raw_high",
        "raw_low",
        "raw_close",
        "raw_volume",
        "raw_traded_value",
        "previous_close",
        "last_price",
        "transaction_count",
        "adjusted_open",
        "adjusted_high",
        "adjusted_low",
        "adjusted_close",
        "adjusted_volume",
        "price_factor",
        "volume_factor",
    ]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for bar in sorted(bars, key=lambda item: (item.trade_date, item.symbol)):
            writer.writerow(
                {
                    "trade_date": bar.trade_date.isoformat(),
                    "symbol": bar.symbol,
                    "isin": bar.isin or "",
                    "series": bar.series,
                    "source_format": bar.source_format,
                    "raw_open": str(bar.raw_open),
                    "raw_high": str(bar.raw_high),
                    "raw_low": str(bar.raw_low),
                    "raw_close": str(bar.raw_close),
                    "raw_volume": str(bar.raw_volume),
                    "raw_traded_value": str(bar.raw_traded_value),
                    "previous_close": str(bar.previous_close),
                    "last_price": str(bar.last_price),
                    "transaction_count": bar.transaction_count,
                    "adjusted_open": str(bar.adjusted_open),
                    "adjusted_high": str(bar.adjusted_high),
                    "adjusted_low": str(bar.adjusted_low),
                    "adjusted_close": str(bar.adjusted_close),
                    "adjusted_volume": str(bar.adjusted_volume),
                    "price_factor": str(bar.price_factor),
                    "volume_factor": str(bar.volume_factor),
                }
            )
    return output


def write_processed_dataset_report(
    report: ProcessedDatasetReport,
    output_path: str | Path,
    *,
    project_root: str | Path,
) -> Path:
    """Write a committed manifest for a local processed dataset build."""

    output = Path(output_path)
    root = Path(project_root)
    action_counts = Counter(action.action_type for action in report.corporate_actions)
    source_counts = Counter(bar.source_format for bar in report.bars)
    adjusted_count = sum(1 for bar in report.bars if bar.price_factor != Decimal("1"))
    rows_per_symbol = Counter(bar.symbol for bar in report.bars)

    lines = [
        "# Processed Dataset Build V0",
        "",
        "**Status:** Evidence artifact",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Dataset version | `{report.dataset_version}` |",
        f"| Frozen universe symbols | {len(report.universe_symbols)} |",
        f"| Ordinary sessions | {len(report.ordinary_sessions_checked)} |",
        f"| Processed bars | {len(report.bars)} |",
        f"| Bars with non-unit price factor | {adjusted_count} |",
        f"| Corporate actions parsed for selected symbols | {len(report.corporate_actions)} |",
        f"| Market-data missing files | {len(report.market_validation.missing_files)} |",
        f"| Market-data file failures | {len(report.market_validation.file_failures)} |",
        f"| Market-data row rejections | {len(report.market_validation.rejected_rows)} |",
        f"| Processed CSV | `{_display_path(report.output_path, root)}` |",
        f"| Processed CSV SHA-256 | `{report.output_sha256}` |",
        "",
        "## Source Formats",
        "",
        "| Source | Bars |",
        "| --- | ---: |",
    ]
    for source, count in sorted(source_counts.items()):
        lines.append(f"| {source} | {count} |")

    lines.extend(
        [
            "",
            "## Corporate Actions",
            "",
            "| Type | Count |",
            "| --- | ---: |",
        ]
    )
    for action_type in CorporateActionType:
        lines.append(f"| {action_type.name} | {action_counts[action_type]} |")

    supported = [
        action
        for action in report.corporate_actions
        if action.action_type in {CorporateActionType.SPLIT, CorporateActionType.BONUS}
    ]
    lines.extend(
        [
            "",
            "## Supported Adjustments Applied",
            "",
        ]
    )
    if supported:
        lines.extend(
            [
                "| Symbol | Ex-Date | Type | Purpose | Price Factor | Volume Factor |",
                "| --- | --- | --- | --- | ---: | ---: |",
            ]
        )
        for action in supported:
            lines.append(
                f"| {action.symbol} | {action.ex_date} | {action.action_type.name} | "
                f"{_md(action.purpose)} | {action.price_adjustment_factor} | "
                f"{action.volume_adjustment_factor} |"
            )
    else:
        lines.append("None.")

    lines.extend(
        [
            "",
            "## Rows Per Symbol",
            "",
            "| Symbol | Rows |",
            "| --- | ---: |",
        ]
    )
    for symbol in report.universe_symbols:
        lines.append(f"| {symbol} | {rows_per_symbol[symbol]} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This report records a reproducible local processed-dataset build for the",
            "already frozen V0 universe. The processed CSV is deliberately not tracked",
            "in git; the committed evidence is this manifest, including row counts,",
            "corporate-action adjustments, and a content hash.",
            "",
        ]
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def _selected_canonical_bars(
    bars: Iterable[CanonicalEquityBar],
    symbols: tuple[str, ...],
) -> tuple[CanonicalEquityBar, ...]:
    symbol_set = set(symbols)
    selected = [bar for bar in bars if bar.symbol in symbol_set]
    seen: set[tuple[str, date]] = set()
    for bar in selected:
        key = (bar.symbol, bar.trade_date)
        if key in seen:
            raise ProcessedDatasetError(f"duplicate selected bar for {bar.symbol} {bar.trade_date}")
        seen.add(key)
    return tuple(sorted(selected, key=lambda bar: (bar.trade_date, bar.symbol)))


def _validate_complete_symbol_sessions(
    bars: tuple[CanonicalEquityBar, ...],
    symbols: tuple[str, ...],
    sessions: tuple[TradingSession, ...],
) -> None:
    observed = {(bar.symbol, bar.trade_date) for bar in bars}
    missing = [
        (symbol, session.session_date)
        for symbol in symbols
        for session in sessions
        if (symbol, session.session_date) not in observed
    ]
    if missing:
        examples = ", ".join(f"{symbol} {session_date}" for symbol, session_date in missing[:5])
        raise ProcessedDatasetError(
            f"frozen universe has {len(missing)} missing symbol/session bars; "
            f"examples: {examples}"
        )


def _ohlcv_bar(bar: CanonicalEquityBar) -> OHLCVBar:
    return OHLCVBar(
        symbol=bar.symbol,
        bar_date=bar.trade_date,
        open=bar.open,
        high=bar.high,
        low=bar.low,
        close=bar.close,
        volume=bar.volume,
        isin=bar.isin,
    )


def _processed_bar(
    raw: CanonicalEquityBar,
    adjusted: AdjustedOHLCVBar,
) -> ProcessedEquityBar:
    return ProcessedEquityBar(
        trade_date=raw.trade_date,
        symbol=raw.symbol,
        isin=raw.isin,
        series=raw.series,
        source_format=raw.source_format,
        raw_open=adjusted.raw_open,
        raw_high=adjusted.raw_high,
        raw_low=adjusted.raw_low,
        raw_close=adjusted.raw_close,
        raw_volume=adjusted.raw_volume,
        raw_traded_value=raw.traded_value,
        previous_close=raw.previous_close,
        last_price=raw.last_price,
        transaction_count=raw.transaction_count,
        adjusted_open=adjusted.adjusted_open,
        adjusted_high=adjusted.adjusted_high,
        adjusted_low=adjusted.adjusted_low,
        adjusted_close=adjusted.adjusted_close,
        adjusted_volume=adjusted.adjusted_volume,
        price_factor=adjusted.price_factor,
        volume_factor=adjusted.volume_factor,
    )


def _corporate_action_record(row: dict[str, object]) -> CorporateActionRecord:
    raw_record_date = str(row.get("recDate", "")).strip()
    return CorporateActionRecord(
        symbol=str(row.get("symbol", "")).strip().upper(),
        purpose=str(row.get("subject", "")).strip(),
        ex_date=_parse_nse_date(str(row.get("exDate", "")).strip()),
        record_date=None if raw_record_date in {"", "-"} else _parse_nse_date(raw_record_date),
    )


def _parse_nse_date(value: str) -> date:
    return datetime.strptime(value, "%d-%b-%Y").date()


def _normalise_symbols(symbols: Iterable[str]) -> tuple[str, ...]:
    clean = []
    seen = set()
    for symbol in symbols:
        value = symbol.strip().upper()
        if not value:
            continue
        if value in seen:
            raise ProcessedDatasetError(f"duplicate universe symbol {value}")
        clean.append(value)
        seen.add(value)
    return tuple(clean)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve(strict=False).relative_to(root.resolve(strict=False))).replace("\\", "/")
    except ValueError:
        return str(path)


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
