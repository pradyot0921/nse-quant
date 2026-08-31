"""Post-run round-trip turnover evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from nse_quant.backtest.portfolio import FillSide, PortfolioFill


class TurnoverEvaluationError(RuntimeError):
    """Raised when fills cannot produce a valid long-only turnover report."""


@dataclass(frozen=True)
class AnnualRoundTripCount:
    year: int
    completed_round_trips: int
    evaluated_for_limit: bool


@dataclass(frozen=True)
class TurnoverEvaluation:
    annual_limit: int
    annual_counts: tuple[AnnualRoundTripCount, ...]
    failed_years: tuple[int, ...]
    total_completed_round_trips: int
    total_turnover: Decimal

    @property
    def passed(self) -> bool:
        return not self.failed_years


@dataclass(frozen=True)
class _OpenLot:
    quantity: int


def evaluate_round_trip_turnover(
    fills: Iterable[PortfolioFill],
    *,
    complete_years: Iterable[int],
    annual_limit: int = 30,
) -> TurnoverEvaluation:
    """Count completed long-only round trips by exit year after a run."""

    _validate_positive_int(annual_limit, "annual_limit")
    evaluated_years = frozenset(_years(complete_years))
    open_lots: dict[str, list[_OpenLot]] = {}
    counts: dict[int, int] = {}
    total_turnover = Decimal("0.00")

    for fill in sorted(fills, key=_fill_key):
        total_turnover += fill.turnover
        if fill.side is FillSide.BUY:
            open_lots.setdefault(fill.symbol, []).append(_OpenLot(fill.quantity))
            continue
        counts[fill.trade_date.year] = counts.get(fill.trade_date.year, 0) + (
            _close_lots(open_lots, fill)
        )

    years = sorted(set(counts) | evaluated_years)
    annual_counts = tuple(
        AnnualRoundTripCount(
            year=year,
            completed_round_trips=counts.get(year, 0),
            evaluated_for_limit=year in evaluated_years,
        )
        for year in years
    )
    failed_years = tuple(
        count.year
        for count in annual_counts
        if count.evaluated_for_limit
        and count.completed_round_trips > annual_limit
    )

    return TurnoverEvaluation(
        annual_limit=annual_limit,
        annual_counts=annual_counts,
        failed_years=failed_years,
        total_completed_round_trips=sum(counts.values()),
        total_turnover=total_turnover,
    )


def _close_lots(open_lots: dict[str, list[_OpenLot]], fill: PortfolioFill) -> int:
    lots = open_lots.get(fill.symbol, [])
    remaining = fill.quantity
    completed = 0

    while remaining > 0:
        if not lots:
            raise TurnoverEvaluationError(
                f"SELL {fill.symbol} exceeds open turnover lots"
            )

        lot = lots[0]
        if remaining < lot.quantity:
            lots[0] = _OpenLot(lot.quantity - remaining)
            remaining = 0
            continue

        remaining -= lot.quantity
        completed += 1
        del lots[0]

    return completed


def _fill_key(fill: PortfolioFill) -> tuple[object, int, str, str]:
    return (fill.trade_date, fill.sequence, fill.symbol, fill.side.value)


def _years(values: Iterable[int]) -> tuple[int, ...]:
    years = tuple(values)
    for year in years:
        _validate_positive_int(year, "complete_years")
    return years


def _validate_positive_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")
