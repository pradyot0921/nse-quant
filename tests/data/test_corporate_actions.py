from datetime import date
from decimal import Decimal

import pytest

from nse_quant.data.corporate_actions import (
    CorporateActionRecord,
    CorporateActionType,
    factors_for_date,
    parse_corporate_action,
)


EX_DATE = date(2026, 8, 19)


def record(purpose, symbol="ABC", ex_date=EX_DATE):
    return CorporateActionRecord(symbol=symbol, purpose=purpose, ex_date=ex_date)


def test_parse_split_from_face_value_change():
    action = parse_corporate_action(
        record("Stock split from Rs. 10/- to Rs. 5/-")
    )

    assert action.action_type == CorporateActionType.SPLIT
    assert action.price_adjustment_factor == Decimal("0.5")
    assert action.volume_adjustment_factor == Decimal("2")
    assert action.ratio_numerator == Decimal("10")
    assert action.ratio_denominator == Decimal("5")


def test_parse_split_from_subdivision_text():
    action = parse_corporate_action(
        record("Sub-division of equity shares from Rs. 10/- to Re. 1/-")
    )

    assert action.action_type == CorporateActionType.SPLIT
    assert action.price_adjustment_factor == Decimal("0.1")
    assert action.volume_adjustment_factor == Decimal("10")


def test_parse_one_for_one_bonus_adjusts_price_and_volume():
    action = parse_corporate_action(record("Bonus issue in the ratio of 1:1"))

    assert action.action_type == CorporateActionType.BONUS
    assert action.price_adjustment_factor == Decimal("0.5")
    assert action.volume_adjustment_factor == Decimal("2")
    assert action.ratio_numerator == Decimal("1")
    assert action.ratio_denominator == Decimal("1")


def test_parse_fractional_bonus_ratio():
    action = parse_corporate_action(record("Bonus shares 3:5"))

    assert action.action_type == CorporateActionType.BONUS
    assert action.price_adjustment_factor == Decimal("0.625")
    assert action.volume_adjustment_factor == Decimal("1.6")


def test_unsupported_action_is_quarantined_without_adjustment():
    action = parse_corporate_action(record("Interim dividend Rs. 2 per share"))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")
    assert "quarantine" in action.note


def test_malformed_split_is_unsupported():
    action = parse_corporate_action(record("Split of equity shares"))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_factors_apply_only_before_ex_date_for_matching_symbol():
    split = parse_corporate_action(record("Split from Rs. 10/- to Rs. 5/-"))
    bonus = parse_corporate_action(record("Bonus issue 1:1"))
    other_symbol = parse_corporate_action(
        record("Split from Rs. 10/- to Rs. 2/-", symbol="XYZ")
    )

    before = factors_for_date("ABC", date(2026, 8, 18), [split, bonus, other_symbol])
    on_ex_date = factors_for_date("ABC", EX_DATE, [split, bonus, other_symbol])

    assert before.price == Decimal("0.25")
    assert before.volume == Decimal("4")
    assert on_ex_date.price == Decimal("1")
    assert on_ex_date.volume == Decimal("1")


def test_record_validation_rejects_missing_symbol_or_purpose():
    with pytest.raises(ValueError, match="symbol"):
        CorporateActionRecord(symbol="", purpose="Bonus 1:1", ex_date=EX_DATE)

    with pytest.raises(ValueError, match="purpose"):
        CorporateActionRecord(symbol="ABC", purpose="", ex_date=EX_DATE)
