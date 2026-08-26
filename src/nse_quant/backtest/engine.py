"""Minimal explicit day-loop backtest engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from nse_quant.backtest.data import DailyBars
from nse_quant.backtest.portfolio import (
    PortfolioFill,
    PortfolioSnapshot,
    PortfolioState,
)


class BacktestEngineError(RuntimeError):
    """Raised when the day-loop input is not deterministic."""


@dataclass(frozen=True)
class BacktestResult:
    starting_state: PortfolioState
    ending_state: PortfolioState
    snapshots: tuple[PortfolioSnapshot, ...]

    @property
    def final_snapshot(self) -> PortfolioSnapshot:
        if not self.snapshots:
            raise BacktestEngineError("backtest produced no daily snapshots")
        return self.snapshots[-1]


def run_day_loop(
    daily_bars: Iterable[DailyBars],
    *,
    starting_state: PortfolioState,
    fills: Iterable[PortfolioFill] = (),
) -> BacktestResult:
    """Apply scheduled fills by date and mark NAV once per day."""

    days = tuple(sorted(daily_bars, key=lambda item: item.trade_date))
    if not days:
        raise BacktestEngineError("daily_bars is empty")
    _validate_unique_days(days)

    fills_by_date = _fills_by_date(fills)
    session_dates = {day.trade_date for day in days}
    extra_fill_dates = sorted(set(fills_by_date) - session_dates)
    if extra_fill_dates:
        raise BacktestEngineError(f"fills scheduled for non-session dates: {extra_fill_dates}")

    state = starting_state
    snapshots: list[PortfolioSnapshot] = []
    for day in days:
        state = state.apply_fills(fills_by_date.get(day.trade_date, ()))
        snapshots.append(state.mark_to_market(day.trade_date, day))

    return BacktestResult(
        starting_state=starting_state,
        ending_state=state,
        snapshots=tuple(snapshots),
    )


def _validate_unique_days(days: tuple[DailyBars, ...]) -> None:
    seen: set[date] = set()
    duplicates = []
    for day in days:
        if day.trade_date in seen:
            duplicates.append(day.trade_date)
        seen.add(day.trade_date)
    if duplicates:
        raise BacktestEngineError(f"duplicate backtest days: {duplicates}")


def _fills_by_date(
    fills: Iterable[PortfolioFill],
) -> dict[date, tuple[PortfolioFill, ...]]:
    grouped: dict[date, list[PortfolioFill]] = {}
    for fill in fills:
        grouped.setdefault(fill.trade_date, []).append(fill)
    return {
        trade_date: tuple(
            sorted(
                day_fills,
                key=lambda fill: (fill.sequence, fill.symbol, fill.side.value),
            )
        )
        for trade_date, day_fills in grouped.items()
    }
