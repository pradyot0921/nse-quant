from datetime import date
from decimal import Decimal

import pytest

from nse_quant.backtest.data import BacktestBar, DailyBars
from nse_quant.backtest.portfolio import FillSide, PortfolioState, Position
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


def test_rebalance_loop_retries_unfilled_full_exit_next_session():
    starting_state = PortfolioState(
        cash="0",
        positions=(Position("AAA", 10),),
    )

    result = run_rebalance_loop(
        [
            day(DAY1, {"AAA": ("100", "100")}),
            day(DAY2, {"AAA": ("101", "101")}),
            day(DAY3, {"AAA": ("102", "102")}),
        ],
        starting_state=starting_state,
        desired_symbols_by_signal_date={DAY1: []},
        max_positions=1,
        slippage_rate="0",
        untradeable_symbols_by_date={DAY2: ["AAA"]},
    )

    assert result.executions[0].unfilled_exit_symbols == ("AAA",)
    assert result.executions[0].costs.portfolio_fills == ()
    assert result.snapshots[1].positions[0].quantity == 10
    assert result.executions[1].costs.portfolio_fills[0].side is FillSide.SELL
    assert result.executions[1].costs.portfolio_fills[0].quantity == 10
    assert result.ending_state.positions == ()


def test_rebalance_loop_applies_target_exposure_on_next_session_open():
    starting_state = PortfolioState(
        cash="100",
        positions=(Position("AAA", 10),),
    )

    result = run_rebalance_loop(
        [
            day(DAY1, {"AAA": ("100", "100"), "BBB": ("50", "50")}),
            day(DAY2, {"AAA": ("100", "100"), "BBB": ("50", "50")}),
        ],
        starting_state=starting_state,
        desired_symbols_by_signal_date={DAY1: ["AAA", "BBB"]},
        target_exposure_by_signal_date={DAY1: "0.5"},
        max_positions=2,
        slippage_rate="0",
    )

    assert [
        (fill.side, fill.symbol, fill.quantity)
        for fill in result.executions[0].costs.portfolio_fills
    ] == [
        (FillSide.SELL, "AAA", 7),
        (FillSide.BUY, "BBB", 5),
    ]


def test_rebalance_loop_retries_unfilled_target_exposure_reduction():
    starting_state = PortfolioState(
        cash="0",
        positions=(Position("AAA", 10),),
    )

    result = run_rebalance_loop(
        [
            day(DAY1, {"AAA": ("100", "100")}),
            day(DAY2, {"AAA": ("100", "100")}),
            day(DAY3, {"AAA": ("100", "100")}),
        ],
        starting_state=starting_state,
        desired_symbols_by_signal_date={DAY1: ["AAA"]},
        target_exposure_by_signal_date={DAY1: "0.5"},
        max_positions=1,
        slippage_rate="0",
        untradeable_symbols_by_date={DAY2: ["AAA"]},
    )

    assert result.executions[0].unfilled_exit_symbols == ("AAA",)
    assert result.executions[0].costs.portfolio_fills == ()
    assert result.snapshots[1].positions[0].quantity == 10
    assert [
        (fill.side, fill.symbol, fill.quantity)
        for fill in result.executions[1].costs.portfolio_fills
    ] == [(FillSide.SELL, "AAA", 5)]
    assert result.final_snapshot.positions[0].quantity == 5


def test_rebalance_loop_waits_to_enter_replacement_until_exit_fills():
    starting_state = PortfolioState(
        cash="0",
        positions=(Position("AAA", 10),),
    )

    result = run_rebalance_loop(
        [
            day(DAY1, {"AAA": ("100", "100"), "BBB": ("50", "50")}),
            day(DAY2, {"AAA": ("100", "100"), "BBB": ("50", "50")}),
            day(DAY3, {"AAA": ("100", "100"), "BBB": ("50", "50")}),
        ],
        starting_state=starting_state,
        desired_symbols_by_signal_date={DAY1: ["BBB"]},
        max_positions=1,
        slippage_rate="0",
        untradeable_symbols_by_date={DAY2: ["AAA"]},
    )

    assert result.executions[0].costs.portfolio_fills == ()
    assert [(fill.side, fill.symbol) for fill in result.executions[1].costs.portfolio_fills] == [
        (FillSide.SELL, "AAA"),
        (FillSide.BUY, "BBB"),
    ]
    assert "BBB" in result.ending_state.positions_by_symbol


def test_rebalance_loop_rejects_unknown_signal_dates():
    with pytest.raises(RebalanceLoopError, match="non-session"):
        run_rebalance_loop(
            [day(DAY1, {"AAA": ("90", "90")})],
            starting_state=PortfolioState.starting_cash("1000"),
            desired_symbols_by_signal_date={DAY2: ["AAA"]},
            max_positions=1,
        )


def test_rebalance_loop_rejects_new_signal_while_exit_is_pending():
    starting_state = PortfolioState(
        cash="0",
        positions=(Position("AAA", 10),),
    )

    with pytest.raises(RebalanceLoopError, match="prior exit is pending"):
        run_rebalance_loop(
            [
                day(DAY1, {"AAA": ("100", "100"), "BBB": ("50", "50")}),
                day(DAY2, {"AAA": ("100", "100"), "BBB": ("50", "50")}),
                day(DAY3, {"AAA": ("100", "100"), "BBB": ("50", "50")}),
            ],
            starting_state=starting_state,
            desired_symbols_by_signal_date={DAY1: ["BBB"], DAY2: ["BBB"]},
            max_positions=1,
            slippage_rate="0",
            untradeable_symbols_by_date={DAY2: ["AAA"]},
        )


def test_rebalance_loop_rejects_untradeable_symbols_on_non_session_dates():
    with pytest.raises(RebalanceLoopError, match="non-session"):
        run_rebalance_loop(
            [day(DAY1, {"AAA": ("100", "100")})],
            starting_state=PortfolioState.starting_cash("1000"),
            desired_symbols_by_signal_date={},
            max_positions=1,
            untradeable_symbols_by_date={DAY2: ["AAA"]},
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
