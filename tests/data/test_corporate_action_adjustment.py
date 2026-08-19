from datetime import date
from decimal import Decimal

import pytest

from nse_quant.data.corporate_actions import (
    OHLCVBar,
    CorporateActionRecord,
    CorporateActionType,
    MissingCorporateActionError,
    UnsupportedCorporateActionError,
    adjust_ohlcv_bars,
    parse_corporate_action,
    validate_rights_exclusions,
)


def record(purpose, symbol="ABC", ex_date=date(2026, 8, 19)):
    return CorporateActionRecord(symbol=symbol, purpose=purpose, ex_date=ex_date)


def bar(
    symbol="ABC",
    bar_date=date(2026, 8, 18),
    open="100",
    high="110",
    low="90",
    close="105",
    volume="1000",
    isin="INE000A01010",
):
    return OHLCVBar(
        symbol=symbol,
        bar_date=bar_date,
        open=open,
        high=high,
        low=low,
        close=close,
        volume=volume,
        isin=isin,
    )


def test_buyback_is_ignored_for_price_adjustment():
    action = parse_corporate_action(record("Buy Back"))

    assert action.action_type == CorporateActionType.IGNORED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_validate_rights_exclusions_refuses_rights_for_universe_symbol():
    rights = parse_corporate_action(
        record("Rights 1:4 @ Premium Rs 8/-", ex_date=date(2025, 9, 1))
    )

    with pytest.raises(UnsupportedCorporateActionError, match="rights issue"):
        validate_rights_exclusions(
            ["ABC"],
            [rights],
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )


def test_validate_rights_exclusions_allows_other_symbols():
    rights = parse_corporate_action(record("Rights 1:4 @ Premium Rs 8/-", symbol="XYZ"))

    validate_rights_exclusions(["ABC"], [rights])


def test_adjust_ohlcv_applies_backward_factors_and_preserves_raw_values():
    action = parse_corporate_action(
        record("Bonus 2:1", symbol="PATANJALI", ex_date=date(2025, 9, 11))
    )
    raw_bars = [
        bar(
            symbol="PATANJALI",
            bar_date=date(2025, 9, 10),
            open="1810.00",
            high="1810.00",
            low="1788.00",
            close="1802.00",
            volume="286019",
            isin="INE619A01035",
        ),
        bar(
            symbol="PATANJALI",
            bar_date=date(2025, 9, 11),
            open="602.70",
            high="603.50",
            low="589.50",
            close="598.90",
            volume="2427699",
            isin="INE619A01035",
        ),
    ]

    adjusted = adjust_ohlcv_bars(raw_bars, [action])

    assert adjusted[0].raw_close == Decimal("1802.00")
    assert adjusted[0].adjusted_close == Decimal("600.666667")
    assert adjusted[0].adjusted_volume == Decimal("858057.000000")
    assert adjusted[0].price_factor == Decimal("0.3333333333")
    assert adjusted[0].volume_factor == Decimal("3.0000000000")
    assert adjusted[1].adjusted_open == Decimal("602.700000")
    assert adjusted[1].price_factor == Decimal("1")
    assert adjusted[1].volume_factor == Decimal("1")


def test_adjust_ohlcv_allows_isin_change_with_split_on_same_date():
    action = parse_corporate_action(
        record(
            "Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 5/- Per Share",
            symbol="BEML",
            ex_date=date(2025, 11, 3),
        )
    )
    raw_bars = [
        bar(
            symbol="BEML",
            bar_date=date(2025, 10, 31),
            close="4399.80",
            volume="349959",
            isin="INE258A01016",
        ),
        bar(
            symbol="BEML",
            bar_date=date(2025, 11, 3),
            open="2188.00",
            close="2187.00",
            volume="333246",
            isin="INE258A01024",
        ),
    ]

    adjusted = adjust_ohlcv_bars(raw_bars, [action])

    assert adjusted[0].adjusted_close == Decimal("2199.900000")
    assert adjusted[0].adjusted_volume == Decimal("699918.000000")
    assert adjusted[1].adjusted_open == Decimal("2188.000000")


def test_adjust_ohlcv_refuses_isin_change_with_dividend_on_same_date():
    dividend = parse_corporate_action(
        record("Interim Dividend Rs. 8 Per Share", ex_date=date(2025, 11, 3))
    )
    raw_bars = [
        bar(bar_date=date(2025, 10, 31), isin="INE000A01010"),
        bar(bar_date=date(2025, 11, 3), isin="INE000A01028"),
    ]

    with pytest.raises(MissingCorporateActionError, match="ISIN changed"):
        adjust_ohlcv_bars(raw_bars, [dividend])


def test_adjust_ohlcv_allows_isin_change_with_name_change_on_same_date():
    name_change = parse_corporate_action(
        record("Change In Name", ex_date=date(2025, 11, 3))
    )
    raw_bars = [
        bar(bar_date=date(2025, 10, 31), isin="INE000A01010"),
        bar(bar_date=date(2025, 11, 3), isin="INE000A01028"),
    ]

    adjusted = adjust_ohlcv_bars(raw_bars, [name_change])

    assert adjusted[1].price_factor == Decimal("1")
    assert adjusted[1].volume_factor == Decimal("1")


def test_adjust_ohlcv_refuses_unexplained_isin_change():
    raw_bars = [
        bar(bar_date=date(2025, 10, 31), isin="INE000A01010"),
        bar(bar_date=date(2025, 11, 3), isin="INE000A01028"),
    ]

    with pytest.raises(MissingCorporateActionError, match="ISIN changed"):
        adjust_ohlcv_bars(raw_bars, [])


def test_adjust_ohlcv_rejects_binary_float_prices():
    with pytest.raises(TypeError, match="binary float"):
        bar(open=100.0)
