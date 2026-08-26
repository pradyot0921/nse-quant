from datetime import date

import pytest

from nse_quant.backtest.portfolio import FillSide, PortfolioState, Position
from nse_quant.backtest.rebalance import (
    RebalancePlanError,
    RebalanceReason,
    plan_rebalance_orders,
)


DAY = date(2026, 8, 21)


def state(*positions):
    return PortfolioState(cash="1000", positions=positions)


def position(symbol, quantity):
    return Position(symbol=symbol, quantity=quantity)


def test_rebalance_plans_exits_before_entries():
    plan = plan_rebalance_orders(
        signal_date=DAY,
        current_state=state(
            position("BBB", 20),
            position("AAA", 10),
            position("KEEP", 30),
        ),
        desired_symbols=["KEEP", "CCC", "DDD"],
    )

    assert [(order.sequence, order.side, order.symbol, order.quantity) for order in plan.orders] == [
        (1, FillSide.SELL, "AAA", 10),
        (2, FillSide.SELL, "BBB", 20),
        (3, FillSide.BUY, "CCC", None),
        (4, FillSide.BUY, "DDD", None),
    ]
    assert [order.reason for order in plan.exit_orders] == [
        RebalanceReason.EXIT_NOT_DESIRED,
        RebalanceReason.EXIT_NOT_DESIRED,
    ]
    assert [order.reason for order in plan.entry_orders] == [
        RebalanceReason.ENTER_DESIRED,
        RebalanceReason.ENTER_DESIRED,
    ]


def test_rebalance_preserves_desired_symbol_order_for_entries():
    plan = plan_rebalance_orders(
        signal_date=DAY,
        current_state=state(),
        desired_symbols=["CCC", "AAA", "BBB"],
    )

    assert [order.symbol for order in plan.entry_orders] == ["CCC", "AAA", "BBB"]
    assert plan.desired_symbols == ("CCC", "AAA", "BBB")


def test_rebalance_holds_symbols_already_desired():
    plan = plan_rebalance_orders(
        signal_date=DAY,
        current_state=state(position("AAA", 10), position("BBB", 20)),
        desired_symbols=["AAA", "BBB"],
    )

    assert plan.orders == ()


def test_empty_desired_symbols_exits_all_holdings():
    plan = plan_rebalance_orders(
        signal_date=DAY,
        current_state=state(position("BBB", 20), position("AAA", 10)),
        desired_symbols=[],
    )

    assert [(order.side, order.symbol, order.quantity) for order in plan.orders] == [
        (FillSide.SELL, "AAA", 10),
        (FillSide.SELL, "BBB", 20),
    ]
    assert plan.entry_orders == ()


def test_rebalance_normalizes_desired_symbols_and_rejects_duplicates():
    with pytest.raises(RebalancePlanError, match="duplicate desired symbols"):
        plan_rebalance_orders(
            signal_date=DAY,
            current_state=state(),
            desired_symbols=[" abc ", "ABC"],
        )


def test_rebalance_rejects_invalid_signal_date():
    with pytest.raises(TypeError, match="signal_date"):
        plan_rebalance_orders(
            signal_date="2026-08-21",
            current_state=state(),
            desired_symbols=[],
        )
