from datetime import date
from decimal import Decimal

from nse_quant.backtest.data import BacktestBar, DailyBars
from nse_quant.backtest.portfolio import FillSide, PortfolioState, Position
from nse_quant.backtest.rebalance_loop import run_rebalance_loop
from nse_quant.backtest.turnover import evaluate_round_trip_turnover
from nse_quant.reporting.trade_log import trade_log_rows_from_execution


DAY1 = date(2026, 1, 5)
DAY2 = date(2026, 1, 6)
DAY3 = date(2026, 1, 7)
DAY4 = date(2026, 1, 8)
DAY5 = date(2026, 1, 9)


def bar(trade_date, symbol, open_price, close_price=None):
    open_value = Decimal(open_price)
    close_value = Decimal(close_price or open_price)
    return BacktestBar(
        trade_date=trade_date,
        symbol=symbol,
        adjusted_open=open_value,
        adjusted_high=max(open_value, close_value),
        adjusted_low=min(open_value, close_value),
        adjusted_close=close_value,
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


def test_three_trade_hand_reconciliation_across_accounting_layers():
    result = run_rebalance_loop(
        [
            day(DAY1, {"AAA": ("90", "90"), "BBB": ("109.24", "109.24")}),
            day(DAY2, {"AAA": ("90", "95"), "BBB": ("109.24", "109.24")}),
            day(DAY3, {"AAA": ("96", "97"), "BBB": ("109.24", "109.24")}),
            day(DAY4, {"AAA": ("100", "100"), "BBB": ("109.24", "109.24")}),
            day(DAY5, {"AAA": ("100", "100"), "BBB": ("109.24", "110")}),
        ],
        starting_state=PortfolioState.starting_cash("1000"),
        desired_symbols_by_signal_date={
            DAY1: ["AAA"],
            DAY2: [],
            DAY4: ["BBB"],
        },
        max_positions=1,
        slippage_rate="0",
        untradeable_symbols_by_date={DAY3: ["AAA"]},
    )

    fills = tuple(
        fill for execution in result.executions for fill in execution.costs.portfolio_fills
    )
    assert [
        (
            fill.trade_date,
            fill.sequence,
            fill.side,
            fill.symbol,
            fill.quantity,
            fill.price,
            fill.turnover,
            fill.fees,
        )
        for fill in fills
    ] == [
        (DAY2, 1, FillSide.BUY, "AAA", 11, Decimal("90.00"), Decimal("990.00"), Decimal("1.19")),
        (DAY4, 1, FillSide.SELL, "AAA", 11, Decimal("100.00"), Decimal("1100.00"), Decimal("16.38")),
        (DAY5, 1, FillSide.BUY, "BBB", 9, Decimal("109.24"), Decimal("983.16"), Decimal("1.19")),
    ]

    assert result.executions[1].unfilled_exit_symbols == ("AAA",)
    assert result.executions[1].costs.portfolio_fills == ()
    assert result.snapshots[2].positions == (Position("AAA", 11),)
    assert result.executions[3].sized_orders.requests[0].quantity == 9

    rows = tuple(
        row
        for execution in result.executions
        for row in trade_log_rows_from_execution(execution.costs)
    )
    assert [
        (
            row.trade_date,
            row.side,
            row.symbol,
            row.quantity,
            row.turnover,
            row.stt_buy,
            row.stt_sell,
            row.exchange_transaction_charge,
            row.sebi_turnover_charge,
            row.gst,
            row.stamp_duty,
            row.dp_charges,
            row.total_cost,
        )
        for row in rows
    ] == [
        (
            DAY2,
            FillSide.BUY,
            "AAA",
            11,
            Decimal("990.00"),
            Decimal("1.00"),
            Decimal("0"),
            Decimal("0.03"),
            Decimal("0"),
            Decimal("0.01"),
            Decimal("0.15"),
            Decimal("0"),
            Decimal("1.19"),
        ),
        (
            DAY4,
            FillSide.SELL,
            "AAA",
            11,
            Decimal("1100.00"),
            Decimal("0"),
            Decimal("1.00"),
            Decimal("0.03"),
            Decimal("0"),
            Decimal("0.01"),
            Decimal("0"),
            Decimal("15.34"),
            Decimal("16.38"),
        ),
        (
            DAY5,
            FillSide.BUY,
            "BBB",
            9,
            Decimal("983.16"),
            Decimal("1.00"),
            Decimal("0"),
            Decimal("0.03"),
            Decimal("0"),
            Decimal("0.01"),
            Decimal("0.15"),
            Decimal("0"),
            Decimal("1.19"),
        ),
    ]

    assert [
        (snapshot.trade_date, snapshot.cash, snapshot.holdings_value, snapshot.nav)
        for snapshot in result.snapshots
    ] == [
        (DAY1, Decimal("1000.00"), Decimal("0"), Decimal("1000.00")),
        (DAY2, Decimal("8.81"), Decimal("1045.00"), Decimal("1053.81")),
        (DAY3, Decimal("8.81"), Decimal("1067.00"), Decimal("1075.81")),
        (DAY4, Decimal("1092.43"), Decimal("0"), Decimal("1092.43")),
        (DAY5, Decimal("108.08"), Decimal("990.00"), Decimal("1098.08")),
    ]

    turnover = evaluate_round_trip_turnover(fills, complete_years=(2026,))
    assert turnover.total_completed_round_trips == 1
    assert turnover.total_turnover == Decimal("3073.16")
    assert turnover.passed
