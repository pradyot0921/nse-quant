from dataclasses import replace
from datetime import date
from decimal import Decimal, localcontext
import json
from pathlib import Path

import pytest

from nse_quant.data.corporate_action_events import (
    CorporateActionEvent,
    DuplicateCorporateActionError,
    adjust_ohlcv_events,
    event_components,
    parse_corporate_action_event,
)
from nse_quant.data.corporate_actions import (
    CorporateActionRecord,
    CorporateActionType,
    MissingCorporateActionError,
    OHLCVBar,
    UnsupportedCorporateActionError,
    parse_corporate_action,
)


EX_DATE = date(2015, 3, 19)
PURPOSE = "Bonus 1:1 / Face Value Split - From Rs 10/- Per Share To Rs 5/- Per Share"
FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "techm_2015_multi_action.json"


def record(purpose=PURPOSE, symbol="TECHM"):
    return CorporateActionRecord(symbol, purpose, EX_DATE, date(2015, 3, 20))


def bar(day=date(2015, 3, 18), symbol="TECHM"):
    return OHLCVBar(symbol, day, "100", "120", "80", "100", "1000")


def test_combined_event_preserves_both_components_and_original_metadata():
    source = record()
    event = parse_corporate_action_event(source)
    assert event.source == source
    assert [item.action_type for item in event.components] == [
        CorporateActionType.BONUS, CorporateActionType.SPLIT
    ]
    assert [(item.ratio_numerator, item.ratio_denominator) for item in event.components] == [
        (Decimal("1"), Decimal("1")), (Decimal("10"), Decimal("5"))
    ]
    assert all(item.purpose == PURPOSE for item in event.components)
    adjusted = adjust_ohlcv_events([bar(), bar(EX_DATE), bar(date(2015, 3, 20))], [event])
    assert [item.price_factor for item in adjusted] == [Decimal("0.25"), 1, 1]
    assert [item.volume_factor for item in adjusted] == [4, 1, 1]
    assert adjusted[0].adjusted_volume == Decimal("4000.000000")
    assert adjusted[0].adjusted_close * adjusted[0].adjusted_volume == Decimal("100000")


def test_split_first_and_bonus_first_are_identical():
    reverse = "Face Value Split - From Rs 10/- Per Share To Rs 5/- Per Share and Bonus 1 : 1"
    first = adjust_ohlcv_events([bar()], [parse_corporate_action_event(record())])
    second = adjust_ohlcv_events([bar()], [parse_corporate_action_event(record(reverse))])
    assert first == second


def test_separate_same_date_records_match_combined_and_ignore_input_order():
    events = [parse_corporate_action_event(record("Bonus 1:1")),
              parse_corporate_action_event(record("Stock split from Rs 10 to Rs 5"))]
    expected = adjust_ohlcv_events([bar()], [parse_corporate_action_event(record())])
    assert adjust_ohlcv_events([bar()], events) == expected
    assert adjust_ohlcv_events([bar()], reversed(events)) == expected


@pytest.mark.parametrize("extra", [PURPOSE, "Bonus 1:1", "Bonus 2:1", "Stock split from Rs 10 to Rs 5"])
def test_duplicate_or_overlapping_records_fail_before_adjustment(extra):
    events = [parse_corporate_action_event(record()), parse_corporate_action_event(record(extra))]
    with pytest.raises(DuplicateCorporateActionError):
        adjust_ohlcv_events([bar()], events)


@pytest.mark.parametrize("purpose", [
    "Bonus 1/1 / Stock split from Rs 10 to Rs 5",
    "Bonus 1:0 / Stock split from Rs 10 to Rs 5",
    "Bonus 1:1 / Stock split from Rs 10 to Rs 0",
    "Bonus 1:1 / Stock split from Rs 5 to Rs 10",
    "Bonus 1:1 / Stock split from Rs 5 to Rs 5",
    "Bonus 1:1 and revised 2:1 / Stock split from Rs 10 to Rs 5",
    "Bonus 1:1 / Stock split from Rs 10 to Rs 5 / Rights 1:4",
    "Scheme Of Arrangement / " + PURPOSE,
    "Bonus debentures 1:1 / Stock split from Rs 10 to Rs 5",
    PURPOSE + " subject to revised entitlement",
    "Bonus 1:1 / Stock split from Rs 10 to Rs 5 and from Rs 5 to Rs 2",
    "Bonus 1:1 / unknown action",
    "Dividend / Rights 1:4",
    "Consolidation from Rs 5 to Rs 10",
])
def test_ambiguous_records_are_atomic_quarantine(purpose):
    event = parse_corporate_action_event(record(purpose))
    assert len(event.components) == 1
    assert event.components[0].action_type == CorporateActionType.UNSUPPORTED
    with pytest.raises(UnsupportedCorporateActionError):
        adjust_ohlcv_events([bar()], [event])


def test_hcltech_colon_spacing_is_supported_only_in_new_api():
    source = record("Bonus 1 : 1", "HCLTECH")
    assert parse_corporate_action(source).action_type == CorporateActionType.UNSUPPORTED
    event = parse_corporate_action_event(source)
    assert event.components[0].action_type == CorporateActionType.BONUS
    assert event.components[0].price_adjustment_factor == Decimal("0.5")
    assert event.components[0].purpose == source.purpose


def test_legacy_combined_quarantine_is_unchanged():
    assert parse_corporate_action(record()).action_type == CorporateActionType.UNSUPPORTED


@pytest.mark.parametrize("purpose", ["Bonus 1:2", "Stock split from Rs 10 to Rs 5", "Dividend Rs 5", "Buy Back"])
def test_previously_supported_single_actions_are_unchanged(purpose):
    source = record(purpose)
    assert parse_corporate_action_event(source).components == (parse_corporate_action(source),)


def test_repeating_factors_and_same_date_order_are_deterministic():
    events = [parse_corporate_action_event(record("Bonus 1:2")),
              parse_corporate_action_event(record("Stock split from Rs 3 to Rs 1"))]
    with localcontext() as context:
        context.prec = 9
        first = adjust_ohlcv_events([bar()], reversed(events))
        combined = parse_corporate_action_event(record("Bonus 1:2 / Stock split from Rs 3 to Rs 1"))
        second = adjust_ohlcv_events([bar()], [combined])
    assert first == second
    assert first[0].price_factor == Decimal("0.2222222222")
    assert first[0].volume_factor == Decimal("4.5000000000")


def test_other_symbols_and_ex_date_bars_are_not_adjusted():
    event = parse_corporate_action_event(record())
    assert adjust_ohlcv_events([bar(symbol="OTHER")], [event])[0].price_factor == 1
    assert adjust_ohlcv_events([bar(EX_DATE)], [event])[0].price_factor == 1


def test_multiple_ex_dates_compound_once_in_canonical_order():
    first = parse_corporate_action_event(record())
    later = parse_corporate_action_event(replace(record("Bonus 1:1"), ex_date=date(2015, 4, 1)))
    bars = [bar(), bar(EX_DATE), bar(date(2015, 4, 1))]
    adjusted = adjust_ohlcv_events(bars, [later, first])
    assert adjusted == adjust_ohlcv_events(bars, [first, later])
    assert [item.price_factor for item in adjusted] == [Decimal("0.125"), Decimal("0.5"), 1]
    assert [item.volume_factor for item in adjusted] == [8, 2, 1]


def test_unsupported_component_is_not_hidden_by_another_valid_event():
    events = [parse_corporate_action_event(record()),
              parse_corporate_action_event(record("Rights 1:4"))]
    with pytest.raises(UnsupportedCorporateActionError):
        adjust_ohlcv_events([bar()], events)


def test_event_rejects_metadata_mismatch_and_partial_combined_types():
    event = parse_corporate_action_event(record())
    with pytest.raises(ValueError, match="metadata"):
        CorporateActionEvent(record(), (replace(event.components[0], purpose="other"),))
    with pytest.raises(ValueError, match="one bonus and one split"):
        CorporateActionEvent(record(), (event.components[0], event.components[0]))


def test_real_techm_2015_fixture_adjusts_price_volume_and_record_date_isin():
    fixture = json.loads(FIXTURE.read_text())
    bars = [OHLCVBar("TECHM", date.fromisoformat(row["date"]),
                    row["open"], row["high"], row["low"], row["close"],
                    row["volume"], row["isin"]) for row in fixture["bars"]]
    event = parse_corporate_action_event(record())
    adjusted = adjust_ohlcv_events(bars, [event])
    before = adjusted[0]
    assert (before.adjusted_open, before.adjusted_high, before.adjusted_low, before.adjusted_close) == (
        Decimal("718.5"), Decimal("720"), Decimal("697.5"), Decimal("700.125")
    )
    assert before.adjusted_volume == Decimal("15227544")
    assert all(item.adjusted_close == item.raw_close for item in adjusted[1:])
    missing_record_date = parse_corporate_action_event(replace(record(), record_date=None))
    with pytest.raises(MissingCorporateActionError, match="ISIN changed"):
        adjust_ohlcv_events(bars, [missing_record_date])
