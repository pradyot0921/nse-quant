"""Performance metrics for aligned strategy NAV and benchmark TRI series."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext
from typing import Iterable

from nse_quant.backtest.portfolio import PortfolioSnapshot
from nse_quant.data.benchmark import TriBenchmarkBar


METRIC = Decimal("0.000001")
ZERO = Decimal("0")
ONE = Decimal("1")
TRADING_SESSIONS_PER_YEAR = Decimal("252")
CALENDAR_DAYS_PER_YEAR = Decimal("365")


class PerformanceReportError(RuntimeError):
    """Raised when strategy and benchmark series cannot be compared."""


@dataclass(frozen=True)
class PerformanceSummary:
    start_date: date
    end_date: date
    observations: int
    strategy_start_nav: Decimal
    strategy_end_nav: Decimal
    benchmark_start_tri: Decimal
    benchmark_end_tri: Decimal
    strategy_total_return: Decimal
    benchmark_total_return: Decimal
    strategy_cagr: Decimal
    benchmark_cagr: Decimal
    strategy_annualized_volatility: Decimal
    benchmark_annualized_volatility: Decimal
    strategy_sharpe: Decimal
    benchmark_sharpe: Decimal
    strategy_sortino: Decimal
    benchmark_sortino: Decimal
    strategy_calmar: Decimal
    benchmark_calmar: Decimal
    strategy_max_drawdown: Decimal
    benchmark_max_drawdown: Decimal
    drawdown_gate_passed: bool


def summarize_performance(
    strategy_snapshots: Iterable[PortfolioSnapshot],
    benchmark_bars: Iterable[TriBenchmarkBar],
) -> PerformanceSummary:
    """Compare daily strategy NAV with benchmark TRI over identical dates."""

    snapshots = tuple(sorted(strategy_snapshots, key=lambda item: item.trade_date))
    if len(snapshots) < 2:
        raise PerformanceReportError("at least two strategy snapshots are required")
    _validate_unique_dates((snapshot.trade_date for snapshot in snapshots), "strategy")

    benchmark_by_date = _benchmark_by_date(benchmark_bars)
    missing_dates = tuple(
        snapshot.trade_date
        for snapshot in snapshots
        if snapshot.trade_date not in benchmark_by_date
    )
    if missing_dates:
        raise PerformanceReportError(f"missing benchmark dates: {missing_dates}")

    nav_values = tuple(_positive_decimal(snapshot.nav, "strategy NAV") for snapshot in snapshots)
    tri_values = tuple(
        _positive_decimal(
            benchmark_by_date[snapshot.trade_date].total_return_index,
            "benchmark TRI",
        )
        for snapshot in snapshots
    )
    dates = tuple(snapshot.trade_date for snapshot in snapshots)
    elapsed_days = (dates[-1] - dates[0]).days
    if elapsed_days <= 0:
        raise PerformanceReportError("performance period must span at least one day")

    strategy_returns = _period_returns(nav_values)
    benchmark_returns = _period_returns(tri_values)
    strategy_cagr = _cagr(nav_values, elapsed_days)
    benchmark_cagr = _cagr(tri_values, elapsed_days)
    strategy_max_drawdown = _max_drawdown(nav_values)
    benchmark_max_drawdown = _max_drawdown(tri_values)
    return PerformanceSummary(
        start_date=dates[0],
        end_date=dates[-1],
        observations=len(dates),
        strategy_start_nav=nav_values[0],
        strategy_end_nav=nav_values[-1],
        benchmark_start_tri=tri_values[0],
        benchmark_end_tri=tri_values[-1],
        strategy_total_return=_metric(_total_return(nav_values)),
        benchmark_total_return=_metric(_total_return(tri_values)),
        strategy_cagr=_metric(strategy_cagr),
        benchmark_cagr=_metric(benchmark_cagr),
        strategy_annualized_volatility=_metric(
            _annualized_volatility_from_returns(strategy_returns)
        ),
        benchmark_annualized_volatility=_metric(
            _annualized_volatility_from_returns(benchmark_returns)
        ),
        strategy_sharpe=_metric(_sharpe(strategy_returns)),
        benchmark_sharpe=_metric(_sharpe(benchmark_returns)),
        strategy_sortino=_metric(_sortino(strategy_returns)),
        benchmark_sortino=_metric(_sortino(benchmark_returns)),
        strategy_calmar=_metric(_calmar(strategy_cagr, strategy_max_drawdown)),
        benchmark_calmar=_metric(_calmar(benchmark_cagr, benchmark_max_drawdown)),
        strategy_max_drawdown=_metric(strategy_max_drawdown),
        benchmark_max_drawdown=_metric(benchmark_max_drawdown),
        drawdown_gate_passed=strategy_max_drawdown <= benchmark_max_drawdown,
    )


def _benchmark_by_date(
    benchmark_bars: Iterable[TriBenchmarkBar],
) -> dict[date, TriBenchmarkBar]:
    bars = tuple(benchmark_bars)
    if not bars:
        raise PerformanceReportError("benchmark bars are empty")
    _validate_unique_dates((bar.trade_date for bar in bars), "benchmark")
    return {bar.trade_date: bar for bar in bars}


def _validate_unique_dates(values: Iterable[date], label: str) -> None:
    seen: set[date] = set()
    duplicates = []
    for value in values:
        if value in seen:
            duplicates.append(value)
        seen.add(value)
    if duplicates:
        raise PerformanceReportError(f"duplicate {label} dates: {duplicates}")


def _positive_decimal(value: Decimal, field_name: str) -> Decimal:
    if value <= ZERO:
        raise PerformanceReportError(f"{field_name} must be positive")
    return value


def _total_return(values: tuple[Decimal, ...]) -> Decimal:
    return values[-1] / values[0] - ONE


def _cagr(values: tuple[Decimal, ...], elapsed_days: int) -> Decimal:
    with localcontext() as context:
        context.prec = 34
        ratio = values[-1] / values[0]
        exponent = CALENDAR_DAYS_PER_YEAR / Decimal(elapsed_days)
        return (ratio.ln() * exponent).exp() - ONE


def _annualized_volatility(values: tuple[Decimal, ...]) -> Decimal:
    return _annualized_volatility_from_returns(_period_returns(values))


def _annualized_volatility_from_returns(returns: tuple[Decimal, ...]) -> Decimal:
    if len(returns) < 2:
        return ZERO
    mean_return = sum(returns, ZERO) / Decimal(len(returns))
    variance = sum(
        ((value - mean_return) * (value - mean_return) for value in returns),
        ZERO,
    ) / Decimal(len(returns) - 1)
    return variance.sqrt() * TRADING_SESSIONS_PER_YEAR.sqrt()


def _annualized_mean_return(returns: tuple[Decimal, ...]) -> Decimal:
    if not returns:
        return ZERO
    return (sum(returns, ZERO) / Decimal(len(returns))) * TRADING_SESSIONS_PER_YEAR


def _sharpe(returns: tuple[Decimal, ...]) -> Decimal:
    volatility = _annualized_volatility_from_returns(returns)
    if volatility == ZERO:
        return ZERO
    return _annualized_mean_return(returns) / volatility


def _sortino(returns: tuple[Decimal, ...]) -> Decimal:
    downside = tuple(value for value in returns if value < ZERO)
    if not downside:
        return ZERO
    downside_variance = sum((value * value for value in downside), ZERO) / Decimal(
        len(downside)
    )
    downside_deviation = downside_variance.sqrt() * TRADING_SESSIONS_PER_YEAR.sqrt()
    if downside_deviation == ZERO:
        return ZERO
    return _annualized_mean_return(returns) / downside_deviation


def _calmar(cagr: Decimal, max_drawdown: Decimal) -> Decimal:
    if max_drawdown == ZERO:
        return ZERO
    return cagr / max_drawdown


def _period_returns(values: tuple[Decimal, ...]) -> tuple[Decimal, ...]:
    return tuple(
        values[index] / values[index - 1] - ONE
        for index in range(1, len(values))
    )


def _max_drawdown(values: tuple[Decimal, ...]) -> Decimal:
    peak = values[0]
    worst = ZERO
    for value in values:
        if value > peak:
            peak = value
        drawdown = ONE - (value / peak)
        if drawdown > worst:
            worst = drawdown
    return worst


def _metric(value: Decimal) -> Decimal:
    return value.quantize(METRIC)
