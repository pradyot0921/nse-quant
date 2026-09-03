from datetime import date
from decimal import Decimal

from nse_quant.backtest.execution import (
    ExecutionFillRequest,
    build_portfolio_fills_with_costs,
)
from nse_quant.backtest.portfolio import FillSide, PortfolioFill, PortfolioSnapshot, Position
from nse_quant.backtest.turnover import evaluate_round_trip_turnover
from nse_quant.reporting.performance import PerformanceSummary
from nse_quant.reporting.phase1_report import (
    DEFAULT_RESEARCH_WARNINGS,
    summarize_return_concentration,
    write_phase1_markdown_report,
)
from nse_quant.strategies.momentum import RegimeExposureSummary


def request(trade_date, symbol, side, quantity, price):
    return ExecutionFillRequest(
        trade_date=trade_date,
        sequence=1,
        symbol=symbol,
        side=side,
        quantity=quantity,
        reference_price=price,
    )


def summary(drawdown_gate_passed=True):
    return PerformanceSummary(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        observations=252,
        strategy_start_nav=Decimal("50000.00"),
        strategy_end_nav=Decimal("55000.00"),
        benchmark_start_tri=Decimal("1000.00"),
        benchmark_end_tri=Decimal("1060.00"),
        strategy_total_return=Decimal("0.100000"),
        benchmark_total_return=Decimal("0.060000"),
        strategy_cagr=Decimal("0.100000"),
        benchmark_cagr=Decimal("0.060000"),
        strategy_annualized_volatility=Decimal("0.150000"),
        benchmark_annualized_volatility=Decimal("0.120000"),
        strategy_sharpe=Decimal("0.600000"),
        benchmark_sharpe=Decimal("0.500000"),
        strategy_sortino=Decimal("0.700000"),
        benchmark_sortino=Decimal("0.400000"),
        strategy_calmar=Decimal("1.250000"),
        benchmark_calmar=Decimal("0.600000"),
        strategy_max_drawdown=Decimal("0.080000"),
        benchmark_max_drawdown=Decimal("0.100000"),
        drawdown_gate_passed=drawdown_gate_passed,
    )


def test_phase1_report_writes_required_sections_and_warnings(tmp_path):
    execution = build_portfolio_fills_with_costs(
        [request(date(2026, 1, 2), "AAA", FillSide.BUY, 10, "100")],
        slippage_rate="0",
    )
    turnover = evaluate_round_trip_turnover(
        execution.portfolio_fills,
        complete_years=(2026,),
    )

    output = write_phase1_markdown_report(
        tmp_path / "report.md",
        experiment_id="B001",
        strategy_name="3-position weekly relative-momentum baseline",
        universe_version="nifty100_v0_20_d037",
        data_version="nifty100_v0_adjusted_ohlcv_d039",
        performance=summary(),
        turnover=turnover,
        execution_costs=(execution,),
        notes=("Synthetic report fixture only.",),
    )

    text = output.read_text(encoding="utf-8")
    assert "# Phase 1 Experiment Report - B001" in text
    assert "| Universe version | `nifty100_v0_20_d037` |" in text
    assert "| Data version | `nifty100_v0_adjusted_ohlcv_d039` |" in text
    assert "| Net return | 0.100000 |" in text
    assert "| Gross P&L | 5001.19 |" in text
    assert "| Net P&L | 5000.00 |" in text
    assert "| Slippage model | not specified |" in text
    assert "| Sharpe | 0.600000 |" in text
    assert "| Sortino | 0.700000 |" in text
    assert "| Calmar | 1.250000 |" in text
    assert "| Cost drag | 0.000024 |" in text
    assert "| Completed trades with P&L | 0 |" in text
    assert "| Win rate | N/A |" in text
    assert "| Benchmark CAGR | 0.060000 |" in text
    assert "| Benchmark Sharpe | 0.500000 |" in text
    assert "| CAGR difference | 0.040000 |" in text
    assert "| Sharpe difference | 0.100000 |" in text
    assert "| Drawdown gate | PASS |" in text
    assert "| Transaction costs | 1.19 |" in text
    assert "- Synthetic report fixture only." in text
    for warning in DEFAULT_RESEARCH_WARNINGS:
        assert f"- {warning}" in text


def test_phase1_report_marks_gate_failures(tmp_path):
    turnover = evaluate_round_trip_turnover([], complete_years=(2026,), annual_limit=30)

    output = write_phase1_markdown_report(
        tmp_path / "report.md",
        experiment_id="B001",
        strategy_name="baseline",
        universe_version="nifty100_v0_20_d037",
        data_version="nifty100_v0_adjusted_ohlcv_d039",
        performance=summary(drawdown_gate_passed=False),
        turnover=turnover,
    )

    text = output.read_text(encoding="utf-8")
    assert "| Drawdown gate | FAIL |" in text
    assert "| Turnover gate | PASS |" in text
    assert "## Notes\n\nNone." in text


def test_phase1_report_writes_trade_outcome_statistics(tmp_path):
    fills = (
        PortfolioFill(date(2026, 1, 2), 1, "AAA", FillSide.BUY, 10, "100.00"),
        PortfolioFill(date(2026, 1, 10), 1, "AAA", FillSide.SELL, 10, "110.00"),
        PortfolioFill(date(2026, 1, 11), 1, "BBB", FillSide.BUY, 10, "100.00"),
        PortfolioFill(date(2026, 1, 20), 1, "BBB", FillSide.SELL, 10, "90.00"),
    )
    snapshots = (
        PortfolioSnapshot(
            trade_date=date(2026, 1, 2),
            cash=Decimal("49000.00"),
            positions=(Position("AAA", 10),),
            holdings_value=Decimal("1000.00"),
            nav=Decimal("50000.00"),
        ),
        PortfolioSnapshot(
            trade_date=date(2026, 1, 10),
            cash=Decimal("50100.00"),
            positions=(),
            holdings_value=Decimal("0.00"),
            nav=Decimal("50100.00"),
        ),
        PortfolioSnapshot(
            trade_date=date(2026, 1, 11),
            cash=Decimal("49100.00"),
            positions=(Position("BBB", 10),),
            holdings_value=Decimal("1000.00"),
            nav=Decimal("50100.00"),
        ),
        PortfolioSnapshot(
            trade_date=date(2026, 1, 20),
            cash=Decimal("50000.00"),
            positions=(),
            holdings_value=Decimal("0.00"),
            nav=Decimal("50000.00"),
        ),
    )
    turnover = evaluate_round_trip_turnover(fills, complete_years=(2026,))

    output = write_phase1_markdown_report(
        tmp_path / "report.md",
        experiment_id="B001",
        strategy_name="baseline",
        universe_version="nifty100_v0_20_d037",
        data_version="nifty100_v0_adjusted_ohlcv_d039",
        performance=summary(),
        turnover=turnover,
        fills=fills,
        portfolio_snapshots=snapshots,
        slippage_model="adverse deterministic slippage 0.05% baseline",
    )

    text = output.read_text(encoding="utf-8")
    assert "| Slippage model | adverse deterministic slippage 0.05% baseline |" in text
    assert "| Completed trades with P&L | 2 |" in text
    assert "| Average holding period days | 8.500000 |" in text
    assert "| Percentage time invested | 0.500000 |" in text
    assert "| Win rate | 0.500000 |" in text
    assert "| Profit factor | 1.000000 |" in text
    assert "| Average winning trade | 100.00 |" in text
    assert "| Average losing trade | -100.00 |" in text
    assert "| Average win / average loss ratio | 1.000000 |" in text
    assert "| Expectancy per completed trade | 0.00 |" in text


def test_phase1_report_writes_b004_regime_and_concentration_sections(tmp_path):
    fills = (
        PortfolioFill(date(2026, 1, 2), 1, "AAA", FillSide.BUY, 10, "100.00"),
        PortfolioFill(date(2026, 1, 10), 1, "AAA", FillSide.SELL, 10, "115.00"),
        PortfolioFill(date(2026, 1, 11), 1, "BBB", FillSide.BUY, 10, "100.00"),
        PortfolioFill(date(2026, 1, 20), 1, "BBB", FillSide.SELL, 10, "110.00"),
    )
    snapshots = (
        PortfolioSnapshot(
            trade_date=date(2026, 12, 31),
            cash=Decimal("56000.00"),
            positions=(),
            holdings_value=Decimal("0.00"),
            nav=Decimal("56000.00"),
        ),
        PortfolioSnapshot(
            trade_date=date(2027, 12, 31),
            cash=Decimal("58000.00"),
            positions=(),
            holdings_value=Decimal("0.00"),
            nav=Decimal("58000.00"),
        ),
    )
    turnover = evaluate_round_trip_turnover(fills, complete_years=(2026, 2027))

    output = write_phase1_markdown_report(
        tmp_path / "report.md",
        experiment_id="B004",
        strategy_name="weekly relative momentum with hysteresis + filter",
        universe_version="nifty100_v0_20_d037",
        data_version="nifty100_v0_adjusted_ohlcv_d039",
        performance=summary(),
        turnover=turnover,
        fills=fills,
        portfolio_snapshots=snapshots,
        complete_years=(2026, 2027),
        regime_exposure=RegimeExposureSummary(
            risk_on_sessions=60,
            risk_off_sessions=40,
            unavailable_sessions=199,
            weekly_state_changes=3,
        ),
        comparison_rows=(
            ("CAGR", "0.150000", "0.136461"),
            ("Maximum drawdown", "0.300000", "0.512654"),
        ),
    )

    text = output.read_text(encoding="utf-8")
    assert "## Market Regime" in text
    assert "| Risk-on sessions | 60 |" in text
    assert "| Risk-off sessions | 40 |" in text
    assert "| Risk-on share after SMA available | 0.600000 |" in text
    assert "| Weekly regime state changes | 3 |" in text
    assert "## Return Concentration" in text
    assert "| Maximum stock positive contribution share | 0.600000 |" in text
    assert "| Maximum calendar-year positive contribution share | 0.750000 |" in text
    assert "## Direct Candidate Comparison" in text
    assert "| CAGR | 0.150000 | 0.136461 |" in text


def test_return_concentration_reproduces_hand_calculated_fixture():
    fills = (
        PortfolioFill(date(2026, 1, 2), 1, "AAA", FillSide.BUY, 10, "100.00"),
        PortfolioFill(date(2026, 1, 10), 1, "AAA", FillSide.SELL, 10, "130.00"),
        PortfolioFill(date(2026, 1, 11), 1, "BBB", FillSide.BUY, 10, "100.00"),
        PortfolioFill(date(2026, 1, 20), 1, "BBB", FillSide.SELL, 10, "120.00"),
        PortfolioFill(date(2026, 1, 21), 1, "CCC", FillSide.BUY, 10, "100.00"),
        PortfolioFill(date(2026, 1, 30), 1, "CCC", FillSide.SELL, 10, "90.00"),
    )
    snapshots = (
        PortfolioSnapshot(date(2026, 12, 31), Decimal("56000.00"), (), Decimal("0.00"), Decimal("56000.00")),
        PortfolioSnapshot(date(2027, 12, 31), Decimal("59000.00"), (), Decimal("0.00"), Decimal("59000.00")),
    )

    summary_result = summarize_return_concentration(
        fills=fills,
        portfolio_snapshots=snapshots,
        starting_nav=Decimal("50000.00"),
        complete_years=(2026, 2027),
    )

    assert summary_result.max_stock_positive_contribution_share == Decimal("0.600000")
    assert summary_result.max_calendar_year_positive_contribution_share == Decimal("0.666667")
