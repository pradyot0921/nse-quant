"""Mechanical weekly momentum ranking signals."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable

from nse_quant.backtest.data import DailyBars


class MomentumSignalError(RuntimeError):
    """Raised when momentum signal inputs are invalid."""


@dataclass(frozen=True)
class MomentumScore:
    signal_date: date
    symbol: str
    rank: int
    momentum: Decimal


@dataclass(frozen=True)
class MomentumSignal:
    signal_date: date
    desired_symbols: tuple[str, ...]
    scores: tuple[MomentumScore, ...]


def generate_weekly_momentum_signals(
    daily_bars: Iterable[DailyBars],
    *,
    universe: Iterable[str],
    lookback_sessions: int = 60,
    max_positions: int = 3,
) -> tuple[MomentumSignal, ...]:
    """Rank symbols on weekly signal dates using adjusted-close momentum."""

    days = tuple(sorted(daily_bars, key=lambda item: item.trade_date))
    _validate_days(days)
    symbols = _symbols(universe)
    _validate_positive_int(lookback_sessions, "lookback_sessions")
    _validate_positive_int(max_positions, "max_positions")

    signal_indices = _weekly_signal_indices(days)
    signals = []
    for index in signal_indices:
        if index < lookback_sessions:
            continue
        scores = _rank_day(
            days[index],
            days[index - lookback_sessions],
            symbols,
        )
        signals.append(
            MomentumSignal(
                signal_date=days[index].trade_date,
                desired_symbols=tuple(
                    score.symbol for score in scores[:max_positions]
                ),
                scores=scores,
            )
        )

    return tuple(signals)


def _rank_day(
    current_day: DailyBars,
    lookback_day: DailyBars,
    symbols: tuple[str, ...],
) -> tuple[MomentumScore, ...]:
    current = current_day.by_symbol
    lookback = lookback_day.by_symbol
    ranked = []

    for symbol in symbols:
        current_bar = current.get(symbol)
        lookback_bar = lookback.get(symbol)
        if current_bar is None or lookback_bar is None:
            continue
        momentum = (
            current_bar.adjusted_close / lookback_bar.adjusted_close - Decimal("1")
        )
        ranked.append((symbol, momentum))

    ranked.sort(key=lambda item: (-item[1], item[0]))
    return tuple(
        MomentumScore(
            signal_date=current_day.trade_date,
            symbol=symbol,
            rank=index,
            momentum=momentum,
        )
        for index, (symbol, momentum) in enumerate(ranked, start=1)
    )


def _weekly_signal_indices(days: tuple[DailyBars, ...]) -> tuple[int, ...]:
    indices = []
    for index, day in enumerate(days):
        if index == len(days) - 1:
            indices.append(index)
            continue
        if (
            day.trade_date.isocalendar()[:2]
            != days[index + 1].trade_date.isocalendar()[:2]
        ):
            indices.append(index)
    return tuple(indices)


def _validate_days(days: tuple[DailyBars, ...]) -> None:
    seen: set[date] = set()
    duplicates = []
    for day in days:
        if day.trade_date in seen:
            duplicates.append(day.trade_date)
        seen.add(day.trade_date)
    if duplicates:
        raise MomentumSignalError(f"duplicate signal days: {duplicates}")


def _symbols(values: Iterable[str]) -> tuple[str, ...]:
    symbols = tuple(sorted({_symbol(value) for value in values}))
    if not symbols:
        raise MomentumSignalError("universe is empty")
    return symbols


def _symbol(value: str) -> str:
    symbol = value.strip().upper() if isinstance(value, str) else ""
    if not symbol:
        raise ValueError("symbol must be non-blank")
    return symbol


def _validate_positive_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")
