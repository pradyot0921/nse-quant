from datetime import date
from decimal import Decimal

import pytest

from nse_quant.backtest.portfolio import PortfolioSnapshot, PortfolioState
from nse_quant.data.benchmark import NIFTY100_TRI_NAME, TriBenchmarkBar
from nse_quant.reporting.performance import (
    PerformanceReportError,
    summarize_performance,
)


def snapshot(trade_date, nav):
    state = PortfolioState.starting_cash(nav)
    return PortfolioSnapshot(
        trade_date=trade_date,
        cash=state.cash,
        positions=(),
        holdings_value=Decimal("0"),
        nav=state.cash,
    )


def benchmark(trade_date, tri):
    return TriBenchmarkBar(
        index_name=NIFTY100_TRI_NAME,
        trade_date=trade_date,
        total_return_index=Decimal(tri),
        net_total_return_index=None,
    )


def test_performance_summary_aligns_strategy_nav_to_benchmark_tri():
    result = summarize_performance(
        [
            snapshot(date(2026, 1, 1), "100.00"),
            snapshot(date(2026, 7, 2), "110.00"),
            snapshot(date(2027, 1, 1), "121.00"),
        ],
        [
            benchmark(date(2026, 1, 1), "1000.00"),
            benchmark(date(2026, 7, 2), "900.00"),
            benchmark(date(2026, 12, 31), "999.00"),
            benchmark(date(2027, 1, 1), "810.00"),
        ],
    )

    assert result.start_date == date(2026, 1, 1)
    assert result.end_date == date(2027, 1, 1)
    assert result.observations == 3
    assert result.strategy_start_nav == Decimal("100.00")
    assert result.strategy_end_nav == Decimal("121.00")
    assert result.benchmark_start_tri == Decimal("1000.00")
    assert result.benchmark_end_tri == Decimal("810.00")
    assert result.strategy_total_return == Decimal("0.210000")
    assert result.benchmark_total_return == Decimal("-0.190000")
    assert result.strategy_cagr == Decimal("0.210000")
    assert result.benchmark_cagr == Decimal("-0.190000")
    assert result.strategy_annualized_volatility == Decimal("0.000000")
    assert result.benchmark_annualized_volatility == Decimal("0.000000")
    assert result.strategy_max_drawdown == Decimal("0.000000")
    assert result.benchmark_max_drawdown == Decimal("0.190000")
    assert result.drawdown_gate_passed


def test_performance_summary_reports_drawdown_gate_failure():
    result = summarize_performance(
        [
            snapshot(date(2026, 1, 1), "100.00"),
            snapshot(date(2026, 1, 2), "80.00"),
            snapshot(date(2026, 1, 3), "90.00"),
        ],
        [
            benchmark(date(2026, 1, 1), "1000.00"),
            benchmark(date(2026, 1, 2), "950.00"),
            benchmark(date(2026, 1, 3), "960.00"),
        ],
    )

    assert result.strategy_max_drawdown == Decimal("0.200000")
    assert result.benchmark_max_drawdown == Decimal("0.050000")
    assert not result.drawdown_gate_passed


def test_performance_summary_requires_benchmark_for_every_strategy_date():
    with pytest.raises(PerformanceReportError, match="missing benchmark dates"):
        summarize_performance(
            [
                snapshot(date(2026, 1, 1), "100.00"),
                snapshot(date(2026, 1, 2), "101.00"),
            ],
            [benchmark(date(2026, 1, 1), "1000.00")],
        )


def test_performance_summary_rejects_duplicate_dates_and_empty_inputs():
    with pytest.raises(PerformanceReportError, match="duplicate strategy dates"):
        summarize_performance(
            [
                snapshot(date(2026, 1, 1), "100.00"),
                snapshot(date(2026, 1, 1), "101.00"),
            ],
            [benchmark(date(2026, 1, 1), "1000.00")],
        )

    with pytest.raises(PerformanceReportError, match="duplicate benchmark dates"):
        summarize_performance(
            [
                snapshot(date(2026, 1, 1), "100.00"),
                snapshot(date(2026, 1, 2), "101.00"),
            ],
            [
                benchmark(date(2026, 1, 1), "1000.00"),
                benchmark(date(2026, 1, 1), "1001.00"),
            ],
        )

    with pytest.raises(PerformanceReportError, match="benchmark bars are empty"):
        summarize_performance(
            [
                snapshot(date(2026, 1, 1), "100.00"),
                snapshot(date(2026, 1, 2), "101.00"),
            ],
            [],
        )

    with pytest.raises(PerformanceReportError, match="at least two"):
        summarize_performance(
            [snapshot(date(2026, 1, 1), "100.00")],
            [benchmark(date(2026, 1, 1), "1000.00")],
        )


def test_performance_summary_rejects_non_positive_series_values():
    with pytest.raises(PerformanceReportError, match="strategy NAV must be positive"):
        summarize_performance(
            [
                snapshot(date(2026, 1, 1), "0.00"),
                snapshot(date(2026, 1, 2), "101.00"),
            ],
            [
                benchmark(date(2026, 1, 1), "1000.00"),
                benchmark(date(2026, 1, 2), "1001.00"),
            ],
        )
