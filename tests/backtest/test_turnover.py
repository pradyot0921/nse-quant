from datetime import date
from decimal import Decimal

import pytest

from nse_quant.backtest.portfolio import FillSide, PortfolioFill
from nse_quant.backtest.turnover import (
    TurnoverEvaluationError,
    evaluate_round_trip_turnover,
)


def fill(trade_date, symbol, side, quantity, price="100", sequence=0):
    return PortfolioFill(
        trade_date=trade_date,
        sequence=sequence,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
    )


def test_turnover_counts_completed_round_trips_by_exit_year():
    result = evaluate_round_trip_turnover(
        [
            fill(date(2026, 1, 5), "AAA", FillSide.BUY, 10),
            fill(date(2026, 1, 20), "AAA", FillSide.SELL, 10),
            fill(date(2027, 2, 1), "BBB", FillSide.BUY, 5),
            fill(date(2027, 2, 15), "BBB", FillSide.SELL, 5),
        ],
        complete_years=[2026, 2027],
    )

    assert result.passed
    assert result.failed_years == ()
    assert [(count.year, count.completed_round_trips) for count in result.annual_counts] == [
        (2026, 1),
        (2027, 1),
    ]
    assert result.total_completed_round_trips == 2
    assert result.total_turnover == Decimal("3000.00")


def test_turnover_evaluates_only_complete_years_against_limit():
    result = evaluate_round_trip_turnover(
        _round_trips(2026, 31) + _round_trips(2027, 31),
        complete_years=[2026],
        annual_limit=30,
    )

    assert not result.passed
    assert result.failed_years == (2026,)
    assert [
        (count.year, count.completed_round_trips, count.evaluated_for_limit)
        for count in result.annual_counts
    ] == [
        (2026, 31, True),
        (2027, 31, False),
    ]


def test_turnover_reports_excess_round_trips_without_blocking_fills():
    result = evaluate_round_trip_turnover(
        _round_trips(2026, 32),
        complete_years=[2026],
        annual_limit=30,
    )

    assert result.total_completed_round_trips == 32
    assert result.failed_years == (2026,)


def test_turnover_counts_a_lot_only_when_fully_closed():
    result = evaluate_round_trip_turnover(
        [
            fill(date(2026, 1, 5), "AAA", FillSide.BUY, 10),
            fill(date(2026, 1, 6), "AAA", FillSide.SELL, 4),
            fill(date(2026, 1, 7), "AAA", FillSide.SELL, 6),
        ],
        complete_years=[2026],
    )

    assert result.annual_counts[0].completed_round_trips == 1


def test_turnover_rejects_sells_without_open_lots():
    with pytest.raises(TurnoverEvaluationError, match="exceeds open"):
        evaluate_round_trip_turnover(
            [fill(date(2026, 1, 5), "AAA", FillSide.SELL, 1)],
            complete_years=[2026],
        )


def test_turnover_rejects_invalid_limits_and_years():
    with pytest.raises(ValueError, match="annual_limit"):
        evaluate_round_trip_turnover([], complete_years=[2026], annual_limit=0)

    with pytest.raises(TypeError, match="complete_years"):
        evaluate_round_trip_turnover([], complete_years=[2026.0])


def _round_trips(year, count):
    fills = []
    for index in range(count):
        symbol = f"S{index:03d}"
        fills.append(
            fill(date(year, 1, 2), symbol, FillSide.BUY, 1, sequence=index * 2)
        )
        fills.append(
            fill(date(year, 1, 3), symbol, FillSide.SELL, 1, sequence=index * 2 + 1)
        )
    return fills
