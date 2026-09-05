"""Opt-in DATA_METHODOLOGY_V1_D078 corporate-action event bundles.

The legacy single-action parser and V0 dataset builder are intentionally not
switched to this API. A new dataset must adopt this methodology explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal, localcontext
import re
from typing import Iterable

from nse_quant.data.corporate_actions import (
    AdjustedOHLCVBar,
    CorporateActionRecord,
    CorporateActionType,
    OHLCVBar,
    ParsedCorporateAction,
    adjust_ohlcv_bars,
    parse_corporate_action,
)


METHODOLOGY_VERSION = "DATA_METHODOLOGY_V1_D078"
_ADJUSTING_TYPES = {CorporateActionType.BONUS, CorporateActionType.SPLIT}
_NUMBER = r"\d+(?:\.\d+)?"
_BONUS = rf"bonus\s+(?P<new>{_NUMBER})\s*:\s*(?P<old>{_NUMBER})"
_MONEY = rf"(?:rs\.?|re\.?|inr)?\s*{_NUMBER}\s*(?:/-)?"
_PER_SHARE = r"(?:\s+per\s+share)?"
_SPLIT = (
    rf"(?:face\s+value\s+split(?:\s*\(sub-division\))?|stock\s+split|"
    rf"sub-division(?:\s+of\s+equity\s+shares)?)\s*-?\s*"
    rf"from\s+{_MONEY}{_PER_SHARE}\s+to\s+{_MONEY}{_PER_SHARE}"
)
_SEPARATOR = r"\s*(?:/|\band\b)\s*"
_COMBINED = re.compile(
    rf"(?:(?P<bonus_first>{_BONUS}){_SEPARATOR}(?P<split_last>{_SPLIT})|"
    rf"(?P<split_first>{_SPLIT}){_SEPARATOR}"
    rf"(?P<bonus_last>bonus\s+{_NUMBER}\s*:\s*{_NUMBER}))"
)


class DuplicateCorporateActionError(ValueError):
    """Raised for duplicate or conflicting same-symbol/date components."""


@dataclass(frozen=True)
class CorporateActionEvent:
    source: CorporateActionRecord
    components: tuple[ParsedCorporateAction, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.components, tuple) or not 1 <= len(self.components) <= 2:
            raise ValueError("an event must contain one or two immutable components")
        types = {component.action_type for component in self.components}
        if len(self.components) == 2 and types != _ADJUSTING_TYPES:
            raise ValueError("a combined event must contain one bonus and one split")
        for component in self.components:
            if (
                component.symbol != self.source.symbol
                or component.ex_date != self.source.ex_date
                or component.record_date != self.source.record_date
                or component.purpose != self.source.purpose
            ):
                raise ValueError("components must preserve the original source metadata")


def parse_corporate_action_event(record: CorporateActionRecord) -> CorporateActionEvent:
    """Parse an entire source record atomically; never retain a partial event."""

    text = " ".join(record.purpose.lower().split())
    if re.search(
        r"\b(?:rights?|demerger|merger|consolidation|debentures?|preference|"
        r"ncrps|ncds?|crps|ocrps|warrants?)\b|scheme of arrangement",
        text,
    ):
        return _quarantine(record, "Unsupported instrument or reorganisation.")

    # Full-string matching prevents extracting a valid leg from ambiguous text.
    combined = _COMBINED.fullmatch(text)
    with localcontext() as context:
        context.prec = 28
        if combined is not None:
            bonus_text = combined.group("bonus_first") or combined.group("bonus_last")
            split_text = combined.group("split_first") or combined.group("split_last")
            bonus = _parse_component(record, re.sub(r"\s*:\s*", ":", bonus_text))
            split = _parse_component(record, split_text)
            if (
                bonus.action_type != CorporateActionType.BONUS
                or split.action_type != CorporateActionType.SPLIT
                or split.ratio_numerator <= split.ratio_denominator
            ):
                return _quarantine(record, "Both combined components must parse safely.")
            return CorporateActionEvent(record, (bonus, split))

        has_split = re.search(r"split|splt|sub[- ]division", text) is not None
        if "bonus" in text and has_split:
            return _quarantine(record, "Combined purpose is outside the exact supported grammar.")
        if re.search(r"\s+/\s+|\band\b", text):
            return _quarantine(record, "Other multi-clause purposes require explicit support.")

        # The isolated NSE 'Bonus 1 : 1' form needs only colon normalization.
        if re.fullmatch(_BONUS, text):
            component = _parse_component(record, re.sub(r"\s*:\s*", ":", text))
        else:
            component = parse_corporate_action(record)
        if (
            component.action_type == CorporateActionType.SPLIT
            and component.ratio_numerator <= component.ratio_denominator
        ):
            return _quarantine(record, "Only a decrease in face value is supported.")
        return CorporateActionEvent(record, (component,))


def event_components(events: Iterable[CorporateActionEvent]) -> tuple[ParsedCorporateAction, ...]:
    """Flatten in canonical order, refusing overlapping adjusting components.

    Repeated source rows and combined-plus-separate rows must not double-adjust
    data. Conflicting same-date ratios also require upstream reconciliation.
    """

    components = []
    seen = set()
    for event in events:
        for component in event.components:
            if component.action_type in _ADJUSTING_TYPES:
                key = (component.symbol, component.ex_date, component.action_type)
                if key in seen:
                    raise DuplicateCorporateActionError(
                        f"{component.symbol}: duplicate or conflicting "
                        f"{component.action_type.value} on {component.ex_date}"
                    )
                seen.add(key)
            components.append(component)
    return tuple(sorted(components, key=lambda item: (
        item.symbol, item.ex_date, item.action_type.value, item.purpose
    )))


def adjust_ohlcv_events(
    bars: Iterable[OHLCVBar], events: Iterable[CorporateActionEvent]
) -> tuple[AdjustedOHLCVBar, ...]:
    """Validate event bundles and reuse established backward OHLCV adjustment."""

    components = event_components(events)
    with localcontext() as context:
        context.prec = 28
        return adjust_ohlcv_bars(bars, components)


def _parse_component(record: CorporateActionRecord, clause: str) -> ParsedCorporateAction:
    parsed = parse_corporate_action(replace(record, purpose=clause))
    return replace(parsed, purpose=record.purpose)


def _quarantine(record: CorporateActionRecord, note: str) -> CorporateActionEvent:
    component = ParsedCorporateAction(
        symbol=record.symbol,
        action_type=CorporateActionType.UNSUPPORTED,
        ex_date=record.ex_date,
        record_date=record.record_date,
        purpose=record.purpose,
        price_adjustment_factor=Decimal("1"),
        volume_adjustment_factor=Decimal("1"),
        note=note,
    )
    return CorporateActionEvent(record, (component,))
