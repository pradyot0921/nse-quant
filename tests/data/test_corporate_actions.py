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
    factors_for_date,
    parse_corporate_action,
    validate_actions,
    validate_rights_exclusions,
)


EX_DATE = date(2026, 8, 19)


def record(purpose, symbol="ABC", ex_date=EX_DATE):
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


def test_name_change_is_ignored_for_price_adjustment():
    action = parse_corporate_action(record("Change in name of the company"))

    assert action.action_type == CorporateActionType.IGNORED
    assert action.price_adjustment_factor == Decimal("1")
    assert action.volume_adjustment_factor == Decimal("1")


def test_buyback_is_ignored_for_price_adjustment():
    action = parse_corporate_action(record("Buy Back"))

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
    rights = parse_corporate_action(
        record("Rights 1:4 @ Premium Rs 8/-", symbol="XYZ")
    )

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


def test_record_validation_rejects_missing_symbol_or_purpose():
    with pytest.raises(ValueError, match="symbol"):
        CorporateActionRecord(symbol="", purpose="Bonus 1:1", ex_date=EX_DATE)

    with pytest.raises(ValueError, match="purpose"):
        CorporateActionRecord(symbol="ABC", purpose="", ex_date=EX_DATE)
