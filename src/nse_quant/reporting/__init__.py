"""Performance reporting modules."""

from nse_quant.reporting.performance import (
    PerformanceReportError,
    PerformanceSummary,
    summarize_performance,
)
from nse_quant.reporting.phase1_report import (
    DEFAULT_RESEARCH_WARNINGS,
    write_phase1_markdown_report,
)
from nse_quant.reporting.trade_log import (
    TradeLogError,
    TradeLogRow,
    trade_log_rows_from_execution,
)

__all__ = [
    "DEFAULT_RESEARCH_WARNINGS",
    "PerformanceReportError",
    "PerformanceSummary",
    "TradeLogError",
    "TradeLogRow",
    "summarize_performance",
    "write_phase1_markdown_report",
    "trade_log_rows_from_execution",
]
