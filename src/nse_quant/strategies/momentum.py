"""Mechanical weekly momentum ranking signals."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Iterable

from nse_quant.backtest.data import DailyBars
from nse_quant.data.benchmark import TriBenchmarkBar


class MomentumSignalError(RuntimeError):
    """Raised when momentum signal inputs are invalid."""


class MarketRegime(StrEnum):
    NOT_AVAILABLE = "NOT_AVAILABLE"
    RISK_ON = "RISK_ON"
    RISK_OFF = "RISK_OFF"


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


@dataclass(frozen=True)
class MarketRegimeSignal:
    signal_date: date
    regime: MarketRegime
    benchmark_tri: Decimal
    sma200: Decimal | None


@dataclass(frozen=True)
class RegimeFilteredMomentumSignal:
    signal_date: date
    desired_symbols: tuple[str, ...]
    scores: tuple[MomentumScore, ...]
    regime: MarketRegime
    benchmark_tri: Decimal
    sma200: Decimal | None


@dataclass(frozen=True)
class RegimeExposureSummary:
    risk_on_sessions: int
    risk_off_sessions: int
    unavailable_sessions: int
    weekly_state_changes: int

    @property
    def available_sessions(self) -> int:
        return self.risk_on_sessions + self.risk_off_sessions

    @property
    def risk_on_share(self) -> Decimal | None:
        if self.available_sessions == 0:
            return None
        return Decimal(self.risk_on_sessions) / Decimal(self.available_sessions)

    @property
    def risk_off_share(self) -> Decimal | None:
        if self.available_sessions == 0:
            return None
        return Decimal(self.risk_off_sessions) / Decimal(self.available_sessions)


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


def generate_weekly_hysteresis_momentum_signals(
    daily_bars: Iterable[DailyBars],
    *,
    universe: Iterable[str],
    lookback_sessions: int = 60,
    max_positions: int = 3,
    entry_rank: int = 3,
    hold_rank: int = 6,
) -> tuple[MomentumSignal, ...]:
    """Rank weekly momentum with explicit entry and hold thresholds."""

    days = tuple(sorted(daily_bars, key=lambda item: item.trade_date))
    _validate_days(days)
    symbols = _symbols(universe)
    _validate_positive_int(lookback_sessions, "lookback_sessions")
    _validate_positive_int(max_positions, "max_positions")
    _validate_positive_int(entry_rank, "entry_rank")
    _validate_positive_int(hold_rank, "hold_rank")
    if entry_rank > hold_rank:
        raise ValueError("entry_rank must be less than or equal to hold_rank")

    signals = []
    previous_desired: tuple[str, ...] = ()
    for index in _weekly_signal_indices(days):
        if index < lookback_sessions:
            continue
        scores = _rank_day(
            days[index],
            days[index - lookback_sessions],
            symbols,
        )
        desired = _hysteresis_desired_symbols(
            scores=scores,
            previous_desired=previous_desired,
            max_positions=max_positions,
            entry_rank=entry_rank,
            hold_rank=hold_rank,
        )
        signals.append(
            MomentumSignal(
                signal_date=days[index].trade_date,
                desired_symbols=desired,
                scores=scores,
            )
        )
        previous_desired = desired

    return tuple(signals)


def generate_weekly_regime_filtered_hysteresis_momentum_signals(
    daily_bars: Iterable[DailyBars],
    *,
    benchmark_bars: Iterable[TriBenchmarkBar],
    universe: Iterable[str],
    lookback_sessions: int = 60,
    max_positions: int = 3,
    entry_rank: int = 3,
    hold_rank: int = 6,
    regime_sma_sessions: int = 200,
) -> tuple[RegimeFilteredMomentumSignal, ...]:
    """Apply the frozen B004 SMA200 regime filter to B003 hysteresis signals."""

    days = tuple(sorted(daily_bars, key=lambda item: item.trade_date))
    _validate_days(days)
    symbols = _symbols(universe)
    _validate_positive_int(lookback_sessions, "lookback_sessions")
    _validate_positive_int(max_positions, "max_positions")
    _validate_positive_int(entry_rank, "entry_rank")
    _validate_positive_int(hold_rank, "hold_rank")
    _validate_positive_int(regime_sma_sessions, "regime_sma_sessions")
    if entry_rank > hold_rank:
        raise ValueError("entry_rank must be less than or equal to hold_rank")

    benchmark_by_date = _benchmark_by_date(benchmark_bars)
    missing_dates = tuple(
        day.trade_date for day in days if day.trade_date not in benchmark_by_date
    )
    if missing_dates:
        raise MomentumSignalError(f"missing benchmark observations: {missing_dates}")

    signals = []
    previous_desired: tuple[str, ...] = ()
    regime_by_date = _daily_regimes(days, benchmark_by_date, regime_sma_sessions)
    for index in _weekly_signal_indices(days):
        if index < lookback_sessions:
            continue
        scores = _rank_day(
            days[index],
            days[index - lookback_sessions],
            symbols,
        )
        regime_signal = regime_by_date[days[index].trade_date]
        if regime_signal.regime is MarketRegime.RISK_ON:
            desired = _hysteresis_desired_symbols(
                scores=scores,
                previous_desired=previous_desired,
                max_positions=max_positions,
                entry_rank=entry_rank,
                hold_rank=hold_rank,
            )
        else:
            desired = ()

        signals.append(
            RegimeFilteredMomentumSignal(
                signal_date=days[index].trade_date,
                desired_symbols=desired,
                scores=scores,
                regime=regime_signal.regime,
                benchmark_tri=regime_signal.benchmark_tri,
                sma200=regime_signal.sma200,
            )
        )
        previous_desired = desired

    return tuple(signals)


def summarize_regime_exposure(
    daily_bars: Iterable[DailyBars],
    *,
    benchmark_bars: Iterable[TriBenchmarkBar],
    weekly_signals: Iterable[RegimeFilteredMomentumSignal] = (),
    regime_sma_sessions: int = 200,
) -> RegimeExposureSummary:
    days = tuple(sorted(daily_bars, key=lambda item: item.trade_date))
    _validate_days(days)
    _validate_positive_int(regime_sma_sessions, "regime_sma_sessions")
    benchmark_by_date = _benchmark_by_date(benchmark_bars)
    missing_dates = tuple(
        day.trade_date for day in days if day.trade_date not in benchmark_by_date
    )
    if missing_dates:
        raise MomentumSignalError(f"missing benchmark observations: {missing_dates}")

    daily_regimes = tuple(
        _daily_regimes(days, benchmark_by_date, regime_sma_sessions).values()
    )
    weekly_regimes = tuple(signal.regime for signal in weekly_signals)
    return RegimeExposureSummary(
        risk_on_sessions=sum(
            1 for signal in daily_regimes if signal.regime is MarketRegime.RISK_ON
        ),
        risk_off_sessions=sum(
            1 for signal in daily_regimes if signal.regime is MarketRegime.RISK_OFF
        ),
        unavailable_sessions=sum(
            1
            for signal in daily_regimes
            if signal.regime is MarketRegime.NOT_AVAILABLE
        ),
        weekly_state_changes=_state_changes(weekly_regimes),
    )


def _hysteresis_desired_symbols(
    *,
    scores: tuple[MomentumScore, ...],
    previous_desired: tuple[str, ...],
    max_positions: int,
    entry_rank: int,
    hold_rank: int,
) -> tuple[str, ...]:
    ranks = {score.symbol: score.rank for score in scores}
    selected = {
        symbol
        for symbol in previous_desired
        if ranks.get(symbol, hold_rank + 1) <= hold_rank
    }

    for score in scores:
        if score.rank > entry_rank or len(selected) >= max_positions:
            break
        selected.add(score.symbol)

    return tuple(score.symbol for score in scores if score.symbol in selected)


def _daily_regimes(
    days: tuple[DailyBars, ...],
    benchmark_by_date: dict[date, TriBenchmarkBar],
    regime_sma_sessions: int,
) -> dict[date, MarketRegimeSignal]:
    regimes = {}
    tri_values: list[Decimal] = []
    for day in days:
        benchmark_tri = benchmark_by_date[day.trade_date].total_return_index
        tri_values.append(benchmark_tri)
        if len(tri_values) < regime_sma_sessions:
            regimes[day.trade_date] = MarketRegimeSignal(
                signal_date=day.trade_date,
                regime=MarketRegime.NOT_AVAILABLE,
                benchmark_tri=benchmark_tri,
                sma200=None,
            )
            continue

        sma = sum(tri_values[-regime_sma_sessions:], Decimal("0")) / Decimal(
            regime_sma_sessions
        )
        regimes[day.trade_date] = MarketRegimeSignal(
            signal_date=day.trade_date,
            regime=(
                MarketRegime.RISK_ON
                if benchmark_tri > sma
                else MarketRegime.RISK_OFF
            ),
            benchmark_tri=benchmark_tri,
            sma200=sma,
        )
    return regimes


def _benchmark_by_date(
    benchmark_bars: Iterable[TriBenchmarkBar],
) -> dict[date, TriBenchmarkBar]:
    bars = tuple(sorted(benchmark_bars, key=lambda item: item.trade_date))
    if not bars:
        raise MomentumSignalError("benchmark bars are empty")
    seen: set[date] = set()
    duplicates = []
    for bar in bars:
        if bar.trade_date in seen:
            duplicates.append(bar.trade_date)
        seen.add(bar.trade_date)
    if duplicates:
        raise MomentumSignalError(f"duplicate benchmark dates: {duplicates}")
    return {bar.trade_date: bar for bar in bars}


def _state_changes(regimes: tuple[MarketRegime, ...]) -> int:
    available = tuple(
        regime for regime in regimes if regime is not MarketRegime.NOT_AVAILABLE
    )
    return sum(
        1
        for index in range(1, len(available))
        if available[index] is not available[index - 1]
    )


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
