from datetime import date
from decimal import Decimal

import pytest

from nse_quant.data.corporate_actions import (
    CorporateActionRecord,
    CorporateActionType,
    UnsupportedCorporateActionError,
    factors_for_date,
    parse_corporate_action,
    validate_actions,
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


@pytest.mark.parametrize(
    ("purpose", "price_factor", "volume_factor"),
    [
        (
            "Face Value Split (Sub-Division) - From Rs 10/- Per Share To Re 1/- Per Share",
            Decimal("0.1"),
            Decimal("10"),
        ),
        (
            "Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 2/- Per Share",
            Decimal("0.2"),
            Decimal("5"),
        ),
        (
            "Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 5/- Per Share",
            Decimal("0.5"),
            Decimal("2"),
        ),
        (
            "Face Value Split (Sub-Division) - From Rs 2/- Per Share To Re 1/- Per Share",
            Decimal("0.5"),
            Decimal("2"),
        ),
        (
            "Face Value Split (Sub-Division) - From Rs 5/- Per Share To Re 1/- Per Share",
            Decimal("0.2"),
            Decimal("5"),
        ),
        (
            "Face Value Split (Sub-Division) - From Rs 5/- Per Share To Rs 2/- Per Share",
            Decimal("0.4"),
            Decimal("2.5"),
        ),
        (
            "Face Value Split (Sub-Division) - From Rs 4/- Per Share To Rs 2/- Per Share",
            Decimal("0.5"),
            Decimal("2"),
        ),
        (
            "Fv Splt Frm Rs 10 To Rs 2",
            Decimal("0.2"),
            Decimal("5"),
        ),
        (
            "Fv Splt Frm Rs 10 To Re 1",
            Decimal("0.1"),
            Decimal("10"),
        ),
        (
            "Fv Splt Frm Rs 5 To Re 1",
            Decimal("0.2"),
            Decimal("5"),
        ),
    ],
)
def test_real_nse_split_purposes_parse_from_face_value_per_share(
    purpose, price_factor, volume_factor
):
    action = parse_corporate_action(record(purpose))

    assert action.action_type == CorporateActionType.SPLIT
    assert action.price_adjustment_factor == price_factor
    assert action.volume_adjustment_factor == volume_factor


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


def test_bonus_ratio_ignores_slash_separated_record_date():
    action = parse_corporate_action(
        record("Bonus record date 12/08/2026 ratio 1:1")
    )

    assert action.action_type == CorporateActionType.BONUS
    assert action.price_adjustment_factor == Decimal("0.5")
    assert action.volume_adjustment_factor == Decimal("2")


def test_bonus_ratio_does_not_accept_slash_separator():
    action = parse_corporate_action(record("Bonus issue in the ratio of 1/1"))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_bonus_with_multiple_ratio_tokens_is_unsupported():
    action = parse_corporate_action(record("Bonus issue 1:1 and revised ratio 2:3"))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_combined_split_and_bonus_is_quarantined():
    action = parse_corporate_action(
        record("Face value split from Rs.10/- to Rs.2/- and bonus 1:1")
    )

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")
    assert "Combined split and bonus" in action.note


def test_bonus_repeating_decimal_factor_is_quantized():
    action = parse_corporate_action(record("Bonus issue 1:2"))

    assert action.action_type == CorporateActionType.BONUS
    assert action.price_adjustment_factor == Decimal("0.6666666667")
    assert action.volume_adjustment_factor == Decimal("1.5000000000")


def test_bonus_debentures_are_not_equity_bonus_shares():
    action = parse_corporate_action(record("Bonus debentures 1:1"))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_bonus_preference_issue_is_unsupported():
    action = parse_corporate_action(record("Bonus preference shares 1:1"))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


@pytest.mark.parametrize(
    "purpose",
    [
        "Bonus NCRPS 4:1",
        "Bonus NCD 1:1",
        "Bonus CRPS 1:1",
        "Bonus OCRPS 1:1",
        "Bonus warrants 1:1",
    ],
)
def test_non_equity_bonus_instruments_are_unsupported(purpose):
    action = parse_corporate_action(record(purpose))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_scheme_of_arrangement_bonus_ncrps_is_unsupported():
    action = parse_corporate_action(
        record("Scheme Of Arrangement - Bonus Ncrps 4:1", symbol="TVSMOTOR")
    )

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_unsupported_action_is_quarantined_without_adjustment():
    action = parse_corporate_action(record("Unclear capital reconstruction event"))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")
    assert "quarantine" in action.note


def test_dividend_is_ignored_not_unsupported():
    action = parse_corporate_action(record("Interim dividend Rs. 8 per share"))

    assert action.action_type == CorporateActionType.IGNORED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_known_noop_meeting_is_ignored():
    action = parse_corporate_action(record("AGM and board meeting"))

    assert action.action_type == CorporateActionType.IGNORED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


@pytest.mark.parametrize(
    "purpose",
    [
        "Extra Ordinary General Meeting",
        "Extra-Ordinary General Meeting",
        "Extra- Ordinary General Meeting",
        "Extra Ordinary  General Meeting",
        "Annual General Meetingdividend - Rs 2.5 Per Share",
        "Annual Book Closure",
        "Annual Book Closing",
        "Annual Closing",
        "Buyback",
        "Buyback Of Shares",
    ],
)
def test_real_nse_noop_corpus_purposes_are_ignored(purpose):
    action = parse_corporate_action(record(purpose))

    assert action.action_type == CorporateActionType.IGNORED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_name_change_is_ignored_for_price_adjustment():
    action = parse_corporate_action(record("Change in name of the company"))

    assert action.action_type == CorporateActionType.IGNORED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_malformed_split_is_unsupported():
    action = parse_corporate_action(record("Split of equity shares"))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_consolidation_is_unsupported_for_v1():
    action = parse_corporate_action(record("Consolidation of shares from Rs.1/- to Rs.10/-"))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_rights_issue_is_unsupported_for_v1():
    action = parse_corporate_action(record("Rights issue of equity shares 1:4 at Rs. 10"))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_malformed_bonus_is_unsupported():
    action = parse_corporate_action(record("Bonus record date 12/08/2026"))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_bonus_with_time_like_colon_token_is_unsupported():
    action = parse_corporate_action(record("Bonus issue board meeting at 12:30"))

    assert action.action_type == CorporateActionType.UNSUPPORTED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


@pytest.mark.parametrize(
    ("purpose", "price_factor", "volume_factor"),
    [
        ("Bonus 1: 1", Decimal("0.5"), Decimal("2")),
        ("Bonus 1:1/Dividend- Rs 7 Per Share", Decimal("0.5"), Decimal("2")),
        ("Bonus- 1:2", Decimal("0.6666666667"), Decimal("1.5000000000")),
        ("Bonus:1:1", Decimal("0.5"), Decimal("2")),
    ],
)
def test_real_nse_bonus_punctuation_variants_parse(
    purpose, price_factor, volume_factor
):
    action = parse_corporate_action(record(purpose))

    assert action.action_type == CorporateActionType.BONUS
    assert action.price_adjustment_factor == price_factor
    assert action.volume_adjustment_factor == volume_factor


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


def test_factors_ignore_dividends_while_applying_split():
    dividend_1 = parse_corporate_action(
        record("Interim dividend Rs. 8 per share", ex_date=date(2020, 3, 1))
    )
    split = parse_corporate_action(
        record("Split from Rs. 10/- to Rs. 5/-", ex_date=date(2021, 1, 1))
    )
    dividend_2 = parse_corporate_action(
        record("Final dividend Rs. 12 per share", ex_date=date(2022, 3, 1))
    )

    before_split = factors_for_date(
        "ABC", date(2019, 1, 1), [dividend_1, split, dividend_2]
    )
    after_split = factors_for_date(
        "ABC", date(2025, 1, 1), [dividend_1, split, dividend_2]
    )

    assert before_split.price == Decimal("0.5")
    assert before_split.volume == Decimal("2")
    assert after_split.price == Decimal("1")
    assert after_split.volume == Decimal("1")


def test_validate_actions_refuses_unsupported_matching_action():
    unsupported = parse_corporate_action(
        record("Rights issue of equity shares 1:4 at Rs. 10")
    )

    with pytest.raises(UnsupportedCorporateActionError, match="ABC"):
        validate_actions(["ABC"], [unsupported])


def test_validate_actions_allows_unsupported_action_for_other_symbol():
    unsupported = parse_corporate_action(
        record("Rights issue of equity shares 1:4 at Rs. 10", symbol="XYZ")
    )

    validate_actions(["ABC"], [unsupported])


def test_validate_actions_allows_ignored_matching_action():
    dividend = parse_corporate_action(record("Interim dividend Rs. 8 per share"))

    validate_actions(["ABC"], [dividend])


def test_validate_actions_honors_date_range():
    unsupported = parse_corporate_action(
        record("Rights issue of equity shares 1:4 at Rs. 10", ex_date=date(2020, 1, 1))
    )

    validate_actions(["ABC"], [unsupported], start_date=date(2021, 1, 1))


def test_record_validation_rejects_missing_symbol_or_purpose():
    with pytest.raises(ValueError, match="symbol"):
        CorporateActionRecord(symbol="", purpose="Bonus 1:1", ex_date=EX_DATE)

    with pytest.raises(ValueError, match="purpose"):
        CorporateActionRecord(symbol="ABC", purpose="", ex_date=EX_DATE)
