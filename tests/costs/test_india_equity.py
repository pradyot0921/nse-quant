from datetime import date
from decimal import Decimal

import pytest

from nse_quant.costs.india_equity import Fill, TradeSide, calculate_daily_costs


DAY = date(2026, 8, 19)


def fill(symbol, side, quantity, price, trade_date=DAY):
    return Fill(
        trade_date=trade_date,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=Decimal(price),
    )


def test_zero_fill_costs_are_zero():
    costs = calculate_daily_costs([])

    assert costs.total_turnover == Decimal("0.00")
    assert costs.total_cost == Decimal("0.00")


def test_flat_price_round_trip_loses_exactly_transaction_costs():
    fills = [
        fill("ABC", TradeSide.BUY, 10, "100"),
        fill("ABC", TradeSide.SELL, 10, "100"),
    ]

    costs = calculate_daily_costs(fills)
    gross_pnl = Decimal("0.00")
    net_pnl = gross_pnl - costs.total_cost

    assert costs.total_cost > Decimal("0")
    assert net_pnl == -costs.total_cost


def test_same_symbol_same_day_sell_gets_one_dp_charge():
    fills = [
        fill("ABC", TradeSide.SELL, 5, "100"),
        fill("ABC", TradeSide.SELL, 3, "101"),
    ]

    costs = calculate_daily_costs(fills)

    assert costs.dp_charges == Decimal("15.34")


def test_multi_symbol_same_day_sells_get_one_dp_charge_per_symbol():
    fills = [
        fill("ABC", TradeSide.SELL, 5, "100"),
        fill("XYZ", TradeSide.SELL, 3, "101"),
    ]

    costs = calculate_daily_costs(fills)

    assert costs.dp_charges == Decimal("30.68")


def test_buy_only_trade_has_no_delivery_sell_dp_charge():
    costs = calculate_daily_costs([fill("ABC", TradeSide.BUY, 5, "100")])

    assert costs.dp_charges == Decimal("0.00")


def test_stamp_duty_applies_to_buy_side_only():
    buy_costs = calculate_daily_costs([fill("ABC", TradeSide.BUY, 1000, "100")])
    sell_costs = calculate_daily_costs([fill("ABC", TradeSide.SELL, 1000, "100")])

    assert buy_costs.stamp_duty == Decimal("15.00")
    assert sell_costs.stamp_duty == Decimal("0.00")


def test_stt_uses_explicit_half_up_nearest_rupee_rounding():
    costs = calculate_daily_costs([fill("ABC", TradeSide.BUY, 105, "100")])

    assert costs.stt_buy == Decimal("11")


def test_stt_is_aggregated_and_rounded_once_per_day_per_side():
    fills = [
        fill("ABC", TradeSide.BUY, 105, "50"),
        fill("XYZ", TradeSide.BUY, 105, "50"),
        fill("ABC", TradeSide.SELL, 105, "50"),
        fill("XYZ", TradeSide.SELL, 105, "50"),
    ]

    costs = calculate_daily_costs(fills)

    assert costs.buy_turnover == Decimal("10500.00")
    assert costs.sell_turnover == Decimal("10500.00")
    assert costs.stt_buy == Decimal("11")
    assert costs.stt_sell == Decimal("11")


def test_gst_base_excludes_stamp_duty_and_dp_charges():
    fills = [
        fill("ABC", TradeSide.BUY, 1000, "100"),
        fill("ABC", TradeSide.SELL, 1000, "100"),
    ]

    costs = calculate_daily_costs(fills)
    expected_gst_base = (
        costs.brokerage
        + costs.exchange_transaction_charge
        + costs.sebi_turnover_charge
    )
    wrong_gst_base = expected_gst_base + costs.stamp_duty + costs.dp_charges

    assert costs.gst == (expected_gst_base * Decimal("0.18")).quantize(
        Decimal("0.01")
    )
    assert costs.gst != (wrong_gst_base * Decimal("0.18")).quantize(Decimal("0.01"))


@pytest.mark.parametrize(
    "kwargs, error",
    [
        ({"symbol": "ABC", "side": TradeSide.BUY, "quantity": 0, "price": "100"}, ValueError),
        ({"symbol": "ABC", "side": TradeSide.BUY, "quantity": -1, "price": "100"}, ValueError),
        ({"symbol": "ABC", "side": TradeSide.BUY, "quantity": 1, "price": "0"}, ValueError),
        ({"symbol": "ABC", "side": TradeSide.BUY, "quantity": 1, "price": "-1"}, ValueError),
        ({"symbol": " ", "side": TradeSide.BUY, "quantity": 1, "price": "100"}, ValueError),
        ({"symbol": "ABC", "side": TradeSide.BUY, "quantity": 1, "price": 100.0}, TypeError),
    ],
)
def test_invalid_fill_data_is_rejected(kwargs, error):
    with pytest.raises(error):
        Fill(trade_date=DAY, **kwargs)


def test_mixed_trade_dates_are_rejected_for_single_day_calculation():
    fills = [
        fill("ABC", TradeSide.BUY, 1, "100", date(2026, 8, 19)),
        fill("ABC", TradeSide.SELL, 1, "100", date(2026, 8, 20)),
    ]

    with pytest.raises(ValueError, match="one trade_date"):
        calculate_daily_costs(fills)
