"""Backtest-facing access to the processed V0 equity dataset."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Iterable
import csv


class BacktestDataError(RuntimeError):
    """Raised when processed bars cannot be used by the backtester."""


@dataclass(frozen=True)
class BacktestBar:
    trade_date: date
    symbol: str
    adjusted_open: Decimal
    adjusted_high: Decimal
    adjusted_low: Decimal
    adjusted_close: Decimal
    adjusted_volume: Decimal
    raw_traded_value: Decimal


@dataclass(frozen=True)
class DailyBars:
    trade_date: date
    bars: tuple[BacktestBar, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.trade_date, date):
            raise TypeError("trade_date must be a date")
        symbols = [bar.symbol for bar in self.bars]
        duplicates = sorted({symbol for symbol in symbols if symbols.count(symbol) > 1})
        if duplicates:
            raise BacktestDataError(
                f"duplicate backtest bars for {self.trade_date}: {duplicates}"
            )

    @property
    def by_symbol(self) -> dict[str, BacktestBar]:
        return {bar.symbol: bar for bar in self.bars}

    def require(self, symbol: str) -> BacktestBar:
        clean_symbol = _symbol(symbol)
        try:
            return self.by_symbol[clean_symbol]
        except KeyError:
            raise BacktestDataError(
                f"missing processed bar for {clean_symbol} on {self.trade_date}"
            ) from None


def load_processed_backtest_bars(path: str | Path) -> tuple[BacktestBar, ...]:
    """Load processed adjusted OHLCV rows for backtesting."""

    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        rows = tuple(csv.DictReader(handle))

    bars = tuple(_bar_from_row(row) for row in rows)
    _validate_unique_symbol_dates(bars)
    return tuple(sorted(bars, key=lambda bar: (bar.trade_date, bar.symbol)))


def group_bars_by_date(bars: Iterable[BacktestBar]) -> tuple[DailyBars, ...]:
    """Group processed bars into deterministic daily lookup objects."""

    grouped: dict[date, list[BacktestBar]] = {}
    for bar in bars:
        grouped.setdefault(bar.trade_date, []).append(bar)
    return tuple(
        DailyBars(
            trade_date=trade_date,
            bars=tuple(sorted(day_bars, key=lambda bar: bar.symbol)),
        )
        for trade_date, day_bars in sorted(grouped.items())
    )


def _bar_from_row(row: dict[str, str]) -> BacktestBar:
    return BacktestBar(
        trade_date=date.fromisoformat(row["trade_date"]),
        symbol=_symbol(row["symbol"]),
        adjusted_open=_positive_decimal(row["adjusted_open"], "adjusted_open"),
        adjusted_high=_positive_decimal(row["adjusted_high"], "adjusted_high"),
        adjusted_low=_positive_decimal(row["adjusted_low"], "adjusted_low"),
        adjusted_close=_positive_decimal(row["adjusted_close"], "adjusted_close"),
        adjusted_volume=_positive_decimal(row["adjusted_volume"], "adjusted_volume"),
        raw_traded_value=_positive_decimal(row["raw_traded_value"], "raw_traded_value"),
    )


def _validate_unique_symbol_dates(bars: tuple[BacktestBar, ...]) -> None:
    seen: set[tuple[date, str]] = set()
    duplicates = []
    for bar in bars:
        key = (bar.trade_date, bar.symbol)
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    if duplicates:
        examples = ", ".join(f"{trade_date} {symbol}" for trade_date, symbol in duplicates[:5])
        raise BacktestDataError(f"duplicate processed symbol/date rows: {examples}")


def _positive_decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, float):
        raise TypeError(f"{field_name} must not be a binary float")
    amount = Decimal(str(value).strip())
    if amount <= Decimal("0"):
        raise BacktestDataError(f"{field_name} must be positive")
    return amount


def _symbol(value: str) -> str:
    symbol = value.strip().upper() if isinstance(value, str) else ""
    if not symbol:
        raise BacktestDataError("symbol must be non-blank")
    return symbol
