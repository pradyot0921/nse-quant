"""Markdown report writer for research experiment summaries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

from nse_quant.backtest.execution import ExecutionCostResult
from nse_quant.backtest.portfolio import FillSide, PortfolioFill, PortfolioSnapshot
from nse_quant.backtest.turnover import TurnoverEvaluation
from nse_quant.reporting.performance import PerformanceSummary
from nse_quant.strategies.momentum import (
    RegimeExposureSummary,
    VolatilityExposureSummary,
)


MONEY = Decimal("0.01")
METRIC = Decimal("0.000001")
ZERO = Decimal("0")

DEFAULT_RESEARCH_WARNINGS = (
    "SURVIVORSHIP-BIASED V0 UNIVERSE",
    "NOT POINT-IN-TIME",
    "NOT LIVE-TRADING VALIDATION",
    "SMALL SAMPLE: 20 STOCKS / 2-3 POSITIONS / ONE FIXED UNIVERSE",
    "FEW INDEPENDENT BETS - ESTIMATES HAVE WIDE ERROR BARS",
    "CURRENT 2026 COST SCHEDULE APPLIED RETROSPECTIVELY",
    "UNSUPPORTED-CORPORATE-ACTION FILTER APPLIED",
)

REGIME_SAMPLE_LIMITATION = (
    "REGIME-SAMPLE LIMITATION:",
    "THE RESEARCH WINDOW CONTAINS FEW INDEPENDENT BROAD-MARKET REGIME EPISODES.",
    "THE SMA200 RULE IS EXOGENOUSLY SPECIFIED, BUT ITS OBSERVED PERFORMANCE IN THIS",
    "WINDOW HAS WIDE EPISODE-LEVEL UNCERTAINTY.",
    "DO NOT INTERPRET A GOOD RESULT AS PRECISE ESTIMATION OF REGIME PERFORMANCE.",
)

REALIZED_VOLATILITY_LIMITATION = (
    "REALIZED-VOLATILITY LIMITATION:",
    "B005 USES A 126-SESSION REALIZED-VOLATILITY ESTIMATE ADAPTED FROM",
    "BARROSO AND SANTA-CLARA'S SIX-MONTH MOMENTUM RISK-MANAGEMENT METHOD.",
    "THE 2016-2022 RESEARCH WINDOW PROVIDES A LIMITED NUMBER OF INDEPENDENT",
    "HIGH-VOLATILITY MOMENTUM EPISODES, AND REALIZED VOLATILITY IS ITSELF NOISY.",
    "DO NOT INTERPRET A GOOD RESULT AS PRECISE ESTIMATION OF AN OPTIMAL VOLATILITY",
    "TARGET, LOOKBACK, OR EXPOSURE-SCALING RULE.",
)


@dataclass(frozen=True)
class Phase1ReportStats:
    gross_pnl: Decimal
    net_pnl: Decimal
    transaction_costs: Decimal
    cost_drag: Decimal
    percentage_time_invested: Decimal | None
    completed_trades: int
    average_holding_period_days: Decimal | None
    win_rate: Decimal | None
    profit_factor: Decimal | None
    average_winning_trade: Decimal | None
    average_losing_trade: Decimal | None
    average_win_loss_ratio: Decimal | None
    expectancy_per_completed_trade: Decimal | None


@dataclass(frozen=True)
class ReturnConcentrationSummary:
    max_stock_positive_contribution_share: Decimal | None
    max_calendar_year_positive_contribution_share: Decimal | None


@dataclass(frozen=True)
class _TradeOutcome:
    symbol: str
    entry_date: date
    exit_date: date
    gross_pnl: Decimal
    net_pnl: Decimal


@dataclass
class _OpenTradeLot:
    entry_date: date
    remaining_quantity: int
    entry_turnover_remaining: Decimal
    entry_fees_remaining: Decimal
    gross_pnl: Decimal = ZERO
    net_pnl: Decimal = ZERO


def write_phase1_markdown_report(
    output_path: str | Path,
    *,
    experiment_id: str,
    strategy_name: str,
    universe_version: str,
    data_version: str,
    performance: PerformanceSummary,
    turnover: TurnoverEvaluation,
    execution_costs: Iterable[ExecutionCostResult] = (),
    fills: Iterable[PortfolioFill] = (),
    portfolio_snapshots: Iterable[PortfolioSnapshot] = (),
    slippage_model: str = "not specified",
    regime_exposure: RegimeExposureSummary | None = None,
    volatility_exposure: VolatilityExposureSummary | None = None,
    complete_years: Iterable[int] = (),
    comparison_rows: Iterable[tuple[str, str, str]] = (),
    warnings: Iterable[str] = DEFAULT_RESEARCH_WARNINGS,
    notes: Iterable[str] = (),
) -> Path:
    """Write a deterministic Markdown summary for one research experiment."""

    output = Path(output_path)
    total_costs = _total_costs(execution_costs)
    report_stats = summarize_phase1_report_stats(
        performance=performance,
        transaction_costs=total_costs,
        fills=fills,
        portfolio_snapshots=portfolio_snapshots,
    )
    concentration = summarize_return_concentration(
        fills=fills,
        portfolio_snapshots=portfolio_snapshots,
        starting_nav=performance.strategy_start_nav,
        complete_years=complete_years,
    )
    drawdown_status = "PASS" if performance.drawdown_gate_passed else "FAIL"
    turnover_status = "PASS" if turnover.passed else "FAIL"

    lines = [
        f"# Research Experiment Report - {experiment_id}",
        "",
        "## Identity",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Experiment | `{experiment_id}` |",
        f"| Strategy | {strategy_name} |",
        f"| Universe version | `{universe_version}` |",
        f"| Data version | `{data_version}` |",
        f"| Period | `{performance.start_date}` to `{performance.end_date}` |",
        f"| Observations | {performance.observations} |",
        "",
        "## Portfolio",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Starting capital | {performance.strategy_start_nav} |",
        f"| Ending capital | {performance.strategy_end_nav} |",
        f"| Gross P&L | {report_stats.gross_pnl} |",
        f"| Transaction costs | {report_stats.transaction_costs} |",
        f"| Slippage model | {slippage_model} |",
        f"| Net P&L | {report_stats.net_pnl} |",
        f"| Net return | {performance.strategy_total_return} |",
        f"| CAGR | {performance.strategy_cagr} |",
        f"| Volatility | {performance.strategy_annualized_volatility} |",
        f"| Sharpe | {performance.strategy_sharpe} |",
        f"| Sortino | {performance.strategy_sortino} |",
        f"| Calmar | {performance.strategy_calmar} |",
        f"| Maximum drawdown | {performance.strategy_max_drawdown} |",
        f"| Cost drag | {report_stats.cost_drag} |",
        f"| Completed round trips | {turnover.total_completed_round_trips} |",
        f"| Turnover | {turnover.total_turnover} |",
        f"| Turnover gate | {turnover_status} |",
        f"| Completed trades with P&L | {report_stats.completed_trades} |",
        f"| Average holding period days | {_display(report_stats.average_holding_period_days)} |",
        f"| Percentage time invested | {_display(report_stats.percentage_time_invested)} |",
        f"| Win rate | {_display(report_stats.win_rate)} |",
        f"| Profit factor | {_display(report_stats.profit_factor)} |",
        f"| Average winning trade | {_display(report_stats.average_winning_trade)} |",
        f"| Average losing trade | {_display(report_stats.average_losing_trade)} |",
        f"| Average win / average loss ratio | {_display(report_stats.average_win_loss_ratio)} |",
        f"| Expectancy per completed trade | {_display(report_stats.expectancy_per_completed_trade)} |",
        "",
    ]
    _append_turnover_detail_section(lines, turnover)
    _append_regime_section(lines, regime_exposure)
    _append_volatility_exposure_section(lines, volatility_exposure)
    _append_concentration_section(lines, concentration)
    _append_comparison_section(lines, comparison_rows)
    lines.extend(
        [
        "## Benchmark",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Benchmark start TRI | {performance.benchmark_start_tri} |",
        f"| Benchmark end TRI | {performance.benchmark_end_tri} |",
        f"| Benchmark return | {performance.benchmark_total_return} |",
        f"| Benchmark CAGR | {performance.benchmark_cagr} |",
        f"| Benchmark volatility | {performance.benchmark_annualized_volatility} |",
        f"| Benchmark Sharpe | {performance.benchmark_sharpe} |",
        f"| Benchmark Sortino | {performance.benchmark_sortino} |",
        f"| Benchmark Calmar | {performance.benchmark_calmar} |",
        f"| Benchmark maximum drawdown | {performance.benchmark_max_drawdown} |",
        "",
        "## Relative",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| CAGR difference | {performance.strategy_cagr - performance.benchmark_cagr} |",
        f"| Drawdown difference | {performance.strategy_max_drawdown - performance.benchmark_max_drawdown} |",
        f"| Drawdown difference percentage points | {_percentage_points(performance.strategy_max_drawdown - performance.benchmark_max_drawdown)} |",
        f"| Drawdown worsening relative to benchmark | {_drawdown_relative_change(performance)} |",
        f"| Sharpe difference | {performance.strategy_sharpe - performance.benchmark_sharpe} |",
        f"| Sortino difference | {performance.strategy_sortino - performance.benchmark_sortino} |",
        f"| Calmar difference | {performance.strategy_calmar - performance.benchmark_calmar} |",
        f"| Drawdown gate | {drawdown_status} |",
        "",
        "## Research Warnings",
        "",
        ]
    )
    lines.extend(f"- {warning}" for warning in tuple(warnings))
    lines.extend(["", "## Notes", ""])
    note_tuple = tuple(notes)
    if note_tuple:
        lines.extend(f"- {note}" for note in note_tuple)
    else:
        lines.append("None.")
    lines.append("")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def summarize_phase1_report_stats(
    *,
    performance: PerformanceSummary,
    transaction_costs: Decimal,
    fills: Iterable[PortfolioFill] = (),
    portfolio_snapshots: Iterable[PortfolioSnapshot] = (),
) -> Phase1ReportStats:
    outcomes = _trade_outcomes(fills)
    snapshots = tuple(portfolio_snapshots)
    invested_days = sum(1 for snapshot in snapshots if snapshot.positions)
    snapshot_count = len(snapshots)
    wins = tuple(outcome.net_pnl for outcome in outcomes if outcome.net_pnl > ZERO)
    losses = tuple(outcome.net_pnl for outcome in outcomes if outcome.net_pnl < ZERO)
    completed = len(outcomes)
    net_pnl = _money(performance.strategy_end_nav - performance.strategy_start_nav)
    gross_pnl = _money(net_pnl + transaction_costs)

    return Phase1ReportStats(
        gross_pnl=gross_pnl,
        net_pnl=net_pnl,
        transaction_costs=transaction_costs,
        cost_drag=_ratio(transaction_costs, performance.strategy_start_nav),
        percentage_time_invested=(
            None if snapshot_count == 0 else _metric(Decimal(invested_days) / Decimal(snapshot_count))
        ),
        completed_trades=completed,
        average_holding_period_days=_average_holding_period(outcomes),
        win_rate=(
            None if completed == 0 else _metric(Decimal(len(wins)) / Decimal(completed))
        ),
        profit_factor=_profit_factor(wins, losses),
        average_winning_trade=_average_money(wins),
        average_losing_trade=_average_money(losses),
        average_win_loss_ratio=_average_win_loss_ratio(wins, losses),
        expectancy_per_completed_trade=_average_money(
            tuple(outcome.net_pnl for outcome in outcomes)
        ),
    )


def summarize_return_concentration(
    *,
    fills: Iterable[PortfolioFill] = (),
    portfolio_snapshots: Iterable[PortfolioSnapshot] = (),
    starting_nav: Decimal,
    complete_years: Iterable[int] = (),
) -> ReturnConcentrationSummary:
    outcomes = _trade_outcomes(fills)
    net_by_symbol: dict[str, Decimal] = {}
    for outcome in outcomes:
        net_by_symbol[outcome.symbol] = (
            net_by_symbol.get(outcome.symbol, ZERO) + outcome.net_pnl
        )

    snapshots = tuple(sorted(portfolio_snapshots, key=lambda item: item.trade_date))
    positive_by_year: dict[int, Decimal] = {}
    prior_nav = starting_nav
    for year in tuple(sorted(set(complete_years))):
        year_snapshots = tuple(
            snapshot for snapshot in snapshots if snapshot.trade_date.year == year
        )
        if not year_snapshots:
            continue
        year_end_nav = year_snapshots[-1].nav
        gain = year_end_nav - prior_nav
        if gain > ZERO:
            positive_by_year[year] = gain
        prior_nav = year_end_nav

    return ReturnConcentrationSummary(
        max_stock_positive_contribution_share=_max_positive_share(net_by_symbol),
        max_calendar_year_positive_contribution_share=_max_positive_share(
            positive_by_year
        ),
    )


def _total_costs(execution_costs: Iterable[ExecutionCostResult]) -> Decimal:
    return sum((execution.total_cost for execution in execution_costs), Decimal("0.00"))


def _trade_outcomes(fills: Iterable[PortfolioFill]) -> tuple[_TradeOutcome, ...]:
    open_lots: dict[str, list[_OpenTradeLot]] = {}
    outcomes: list[_TradeOutcome] = []
    for fill in sorted(
        fills,
        key=lambda item: (item.trade_date, item.sequence, item.symbol, item.side.value),
    ):
        if fill.side is FillSide.BUY:
            open_lots.setdefault(fill.symbol, []).append(
                _OpenTradeLot(
                    entry_date=fill.trade_date,
                    remaining_quantity=fill.quantity,
                    entry_turnover_remaining=fill.turnover,
                    entry_fees_remaining=fill.fees,
                )
            )
            continue

        remaining = fill.quantity
        lots = open_lots.get(fill.symbol, [])
        while remaining > 0:
            if not lots:
                raise ValueError(f"SELL {fill.symbol} exceeds open report lots")

            lot = lots[0]
            closed_quantity = min(remaining, lot.remaining_quantity)
            lot_fraction = Decimal(closed_quantity) / Decimal(lot.remaining_quantity)
            fill_fraction = Decimal(closed_quantity) / Decimal(fill.quantity)
            entry_turnover = lot.entry_turnover_remaining * lot_fraction
            entry_fees = lot.entry_fees_remaining * lot_fraction
            sell_turnover = fill.turnover * fill_fraction
            sell_fees = fill.fees * fill_fraction
            gross_pnl = sell_turnover - entry_turnover
            net_pnl = gross_pnl - entry_fees - sell_fees

            lot.gross_pnl += gross_pnl
            lot.net_pnl += net_pnl
            lot.remaining_quantity -= closed_quantity
            lot.entry_turnover_remaining -= entry_turnover
            lot.entry_fees_remaining -= entry_fees
            remaining -= closed_quantity

            if lot.remaining_quantity == 0:
                outcomes.append(
                    _TradeOutcome(
                        symbol=fill.symbol,
                        entry_date=lot.entry_date,
                        exit_date=fill.trade_date,
                        gross_pnl=_money(lot.gross_pnl),
                        net_pnl=_money(lot.net_pnl),
                    )
                )
                del lots[0]

    return tuple(outcomes)


def _max_positive_share(values: dict[object, Decimal]) -> Decimal | None:
    positive = tuple(amount for amount in values.values() if amount > ZERO)
    total = sum(positive, ZERO)
    if total == ZERO:
        return None
    return _metric(max(positive) / total)


def _append_regime_section(
    lines: list[str], regime_exposure: RegimeExposureSummary | None
) -> None:
    if regime_exposure is None:
        return
    lines.extend(
        [
            "## Market Regime",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Risk-on sessions | {regime_exposure.risk_on_sessions} |",
            f"| Risk-off sessions | {regime_exposure.risk_off_sessions} |",
            f"| Regime unavailable sessions | {regime_exposure.unavailable_sessions} |",
            f"| Risk-on share after SMA available | {_display(_optional_metric(regime_exposure.risk_on_share))} |",
            f"| Risk-off share after SMA available | {_display(_optional_metric(regime_exposure.risk_off_share))} |",
            f"| Weekly regime state changes | {regime_exposure.weekly_state_changes} |",
            "",
        ]
    )
    lines.extend(REGIME_SAMPLE_LIMITATION)
    lines.append("")


def _append_volatility_exposure_section(
    lines: list[str], volatility_exposure: VolatilityExposureSummary | None
) -> None:
    if volatility_exposure is None:
        return
    lines.extend(
        [
            "## Volatility Exposure",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Realized-volatility lookback sessions | {volatility_exposure.lookback_sessions} |",
            f"| Target volatility | {_display(_optional_metric(volatility_exposure.target_volatility))} |",
            f"| Minimum exposure multiplier | {_display(volatility_exposure.min_exposure_multiplier)} |",
            f"| Maximum exposure multiplier | {_display(volatility_exposure.max_exposure_multiplier)} |",
            f"| Mean exposure multiplier | {_display(volatility_exposure.mean_exposure_multiplier)} |",
            f"| Median exposure multiplier | {_display(volatility_exposure.median_exposure_multiplier)} |",
            f"| Weekly exposure changes | {volatility_exposure.weekly_exposure_changes} |",
            f"| Zero-exposure session share | {_display(_optional_metric(volatility_exposure.zero_exposure_share))} |",
            f"| Partial-exposure session share | {_display(_optional_metric(volatility_exposure.partial_exposure_share))} |",
            f"| Full-exposure session share | {_display(_optional_metric(volatility_exposure.full_exposure_share))} |",
            "",
        ]
    )
    lines.extend(REALIZED_VOLATILITY_LIMITATION)
    lines.append("")


def _append_turnover_detail_section(
    lines: list[str], turnover: TurnoverEvaluation
) -> None:
    lines.extend(
        [
            "## Annual Turnover Detail",
            "",
            "| Year | Completed round trips | Evaluated for limit | Gate |",
            "| --- | ---: | --- | --- |",
        ]
    )
    failed_years = set(turnover.failed_years)
    for count in turnover.annual_counts:
        gate = (
            "FAIL"
            if count.year in failed_years
            else "PASS"
            if count.evaluated_for_limit
            else "N/A"
        )
        lines.append(
            f"| {count.year} | {count.completed_round_trips} | "
            f"{'yes' if count.evaluated_for_limit else 'no'} | {gate} |"
        )
    lines.append("")


def _append_concentration_section(
    lines: list[str], concentration: ReturnConcentrationSummary
) -> None:
    lines.extend(
        [
            "## Return Concentration",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Maximum stock positive contribution share | {_display(concentration.max_stock_positive_contribution_share)} |",
            f"| Maximum calendar-year positive contribution share | {_display(concentration.max_calendar_year_positive_contribution_share)} |",
            "",
        ]
    )


def _append_comparison_section(
    lines: list[str], comparison_rows: Iterable[tuple[str, str, str]]
) -> None:
    rows = tuple(comparison_rows)
    if not rows:
        return
    lines.extend(
        [
            "## Direct Candidate Comparison",
            "",
            "| Metric | Current candidate | B003 research |",
            "| --- | ---: | ---: |",
        ]
    )
    lines.extend(f"| {metric} | {current} | {b003} |" for metric, current, b003 in rows)
    lines.append("")


def _average_holding_period(outcomes: tuple[_TradeOutcome, ...]) -> Decimal | None:
    if not outcomes:
        return None
    days = sum((outcome.exit_date - outcome.entry_date).days for outcome in outcomes)
    return _metric(Decimal(days) / Decimal(len(outcomes)))


def _profit_factor(wins: tuple[Decimal, ...], losses: tuple[Decimal, ...]) -> Decimal | None:
    loss_total = abs(sum(losses, ZERO))
    if loss_total == ZERO:
        return None
    return _metric(sum(wins, ZERO) / loss_total)


def _average_money(values: tuple[Decimal, ...]) -> Decimal | None:
    if not values:
        return None
    return _money(sum(values, ZERO) / Decimal(len(values)))


def _average_win_loss_ratio(
    wins: tuple[Decimal, ...], losses: tuple[Decimal, ...]
) -> Decimal | None:
    average_win = _average_money(wins)
    average_loss = _average_money(losses)
    if average_win is None or average_loss in (None, ZERO):
        return None
    return _metric(average_win / abs(average_loss))


def _ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
    if denominator == ZERO:
        return ZERO
    return _metric(numerator / denominator)


def _percentage_points(value: Decimal) -> Decimal:
    return _metric(value * Decimal("100"))


def _drawdown_relative_change(performance: PerformanceSummary) -> str:
    if performance.benchmark_max_drawdown == ZERO:
        return "N/A"
    value = (
        performance.strategy_max_drawdown / performance.benchmark_max_drawdown
    ) - Decimal("1")
    return str(_metric(value))


def _display(value: Decimal | None) -> str:
    if value is None:
        return "N/A"
    return str(value)


def _optional_metric(value: Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return _metric(value)


def _metric(value: Decimal) -> Decimal:
    return value.quantize(METRIC, rounding=ROUND_HALF_UP)


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)
