from datetime import date
from decimal import Decimal

import pytest

from nse_quant.backtest.data import BacktestBar, DailyBars
from nse_quant.backtest.portfolio import FillSide, PortfolioState
from nse_quant.backtest.rebalance_loop import (
    RebalanceLoopError,
    run_rebalance_loop,
)


DAY1 = date(2026, 1, 5)
DAY2 = date(2026, 1, 6)
DAY3 = date(2026, 1, 7)


def bar(trade_date, symbol, open_price, close_price=None):
    close = Decimal(close_price or open_price)
    return BacktestBar(
        trade_date=trade_date,
        symbol=symbol,
        adjusted_open=Decimal(open_price),
        adjusted_high=max(Decimal(open_price), close),
        adjusted_low=min(Decimal(open_price), close),
        adjusted_close=close,
        adjusted_volume=Decimal("1000"),
        raw_traded_value=Decimal("100000"),
    )


def day(trade_date, prices):
    return DailyBars(
        trade_date=trade_date,
        bars=tuple(
            bar(trade_date, symbol, open_price, close_price)
            for symbol, (open_price, close_price) in prices.items()
        ),
    )


def test_rebalance_loop_executes_signal_on_next_session_open():
    result = run_rebalance_loop(
        [
            day(DAY1, {"AAA": ("90", "90")}),
            day(DAY2, {"AAA": ("90", "95")}),
        ],
        starting_state=PortfolioState.starting_cash("1000"),
        desired_symbols_by_signal_date={DAY1: ["AAA"]},
        max_positions=1,
        slippage_rate="0",
    )

    assert len(result.executions) == 1
    execution = result.executions[0]
    assert execution.signal_date == DAY1
    assert execution.execution_date == DAY2
    assert [
        (request.trade_date, request.side, request.symbol, request.quantity, request.reference_price)
        for request in execution.sized_orders.requests
    ] == [(DAY2, FillSide.BUY, "AAA", 11, Decimal("90"))]
    assert result.ending_state.positions_by_symbol["AAA"].quantity == 11
    assert result.final_snapshot.trade_date == DAY2


def test_rebalance_loop_uses_current_state_for_later_signals():
    result = run_rebalance_loop(
        [
            day(DAY1, {"AAA": ("90", "90"), "BBB": ("90", "90")}),
            day(DAY2, {"AAA": ("90", "90"), "BBB": ("90", "90")}),
            day(DAY3, {"AAA": ("100", "100"), "BBB": ("90", "90")}),
        ],
        starting_state=PortfolioState.starting_cash("1000"),
        desired_symbols_by_signal_date={
            DAY1: ["AAA"],
            DAY2: ["BBB"],
        },
        max_positions=1,
        slippage_rate="0",
    )

    assert len(result.executions) == 2
    first, second = result.executions
    assert [(order.side, order.symbol) for order in first.plan.orders] == [
        (FillSide.BUY, "AAA")
    ]
    assert [(order.side, order.symbol, order.quantity) for order in second.plan.orders] == [
        (FillSide.SELL, "AAA", 11),
        (FillSide.BUY, "BBB", None),
    ]
    assert result.ending_state.positions_by_symbol["BBB"].quantity > 0
    assert "AAA" not in result.ending_state.positions_by_symbol


def test_rebalance_loop_records_signal_on_final_session_as_unexecuted():
    result = run_rebalance_loop(
        [day(DAY1, {"AAA": ("90", "90")})],
        starting_state=PortfolioState.starting_cash("1000"),
        desired_symbols_by_signal_date={DAY1: ["AAA"]},
        max_positions=1,
        slippage_rate="0",
    )

    assert result.executions == ()
    assert result.unexecuted_signal_dates == (DAY1,)


def test_rebalance_loop_rejects_unknown_signal_dates():
    with pytest.raises(RebalanceLoopError, match="non-session"):
        run_rebalance_loop(
            [day(DAY1, {"AAA": ("90", "90")})],
            starting_state=PortfolioState.starting_cash("1000"),
            desired_symbols_by_signal_date={DAY2: ["AAA"]},
            max_positions=1,
        )


def test_rebalance_loop_rejects_duplicate_daily_dates():
    with pytest.raises(RebalanceLoopError, match="duplicate"):
        run_rebalance_loop(
            [
                day(DAY1, {"AAA": ("90", "90")}),
                day(DAY1, {"BBB": ("90", "90")}),
            ],
            starting_state=PortfolioState.starting_cash("1000"),
            desired_symbols_by_signal_date={},
            max_positions=1,
        )


def test_rebalance_loop_rejects_empty_daily_bars():
    with pytest.raises(RebalanceLoopError, match="empty"):
        run_rebalance_loop(
            [],
            starting_state=PortfolioState.starting_cash("1000"),
            desired_symbols_by_signal_date={},
            max_positions=1,
        )
