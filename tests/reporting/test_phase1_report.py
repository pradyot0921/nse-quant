from datetime import date
from decimal import Decimal

from nse_quant.backtest.execution import (
    ExecutionFillRequest,
    build_portfolio_fills_with_costs,
)
from nse_quant.backtest.portfolio import FillSide
from nse_quant.backtest.turnover import evaluate_round_trip_turnover
from nse_quant.reporting.performance import PerformanceSummary
from nse_quant.reporting.phase1_report import (
    DEFAULT_RESEARCH_WARNINGS,
    write_phase1_markdown_report,
)


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
    assert "| Benchmark CAGR | 0.060000 |" in text
    assert "| CAGR difference | 0.040000 |" in text
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
