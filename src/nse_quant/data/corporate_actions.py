"""Corporate-action parsing and adjustment factors.

Phase 1 intentionally supports only deterministic splits and bonuses. Other
NSE corporate-action purpose strings are returned as unsupported so ingestion
can quarantine them instead of guessing from free text.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
import re
from typing import Iterable


ONE = Decimal("1")


class CorporateActionType(str, Enum):
    SPLIT = "split"
    BONUS = "bonus"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class CorporateActionRecord:
    symbol: str
    purpose: str
    ex_date: date
    record_date: date | None = None

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol is required")
        if not self.purpose.strip():
            raise ValueError("purpose is required")
        object.__setattr__(self, "symbol", self.symbol.strip().upper())
        object.__setattr__(self, "purpose", self.purpose.strip())


@dataclass(frozen=True)
class ParsedCorporateAction:
    symbol: str
    action_type: CorporateActionType
    ex_date: date
    record_date: date | None
    purpose: str
    price_adjustment_factor: Decimal
    volume_adjustment_factor: Decimal
    ratio_numerator: Decimal | None = None
    ratio_denominator: Decimal | None = None
    note: str = ""

    def __post_init__(self) -> None:
        if self.price_adjustment_factor <= 0:
            raise ValueError("price_adjustment_factor must be positive")
        if self.volume_adjustment_factor <= 0:
            raise ValueError("volume_adjustment_factor must be positive")


@dataclass(frozen=True)
class AdjustmentFactors:
    price: Decimal
    volume: Decimal


def parse_corporate_action(record: CorporateActionRecord) -> ParsedCorporateAction:
    """Parse one NSE corporate-action record into deterministic adjustment factors."""

    purpose = _normalise_text(record.purpose)

    if "bonus" in purpose:
        ratio = _parse_ratio(purpose)
        if ratio is not None:
            new_shares, old_shares = ratio
            share_factor = (old_shares + new_shares) / old_shares
            return ParsedCorporateAction(
                symbol=record.symbol,
                action_type=CorporateActionType.BONUS,
                ex_date=record.ex_date,
                record_date=record.record_date,
                purpose=record.purpose,
                price_adjustment_factor=old_shares / (old_shares + new_shares),
                volume_adjustment_factor=share_factor,
                ratio_numerator=new_shares,
                ratio_denominator=old_shares,
                note="Bonus ratio interpreted as new shares per existing shares.",
            )

    if "split" in purpose or "sub-division" in purpose or "sub division" in purpose:
        face_values = _parse_split_face_values(purpose)
        if face_values is not None:
            old_face_value, new_face_value = face_values
            return ParsedCorporateAction(
                symbol=record.symbol,
                action_type=CorporateActionType.SPLIT,
                ex_date=record.ex_date,
                record_date=record.record_date,
                purpose=record.purpose,
                price_adjustment_factor=new_face_value / old_face_value,
                volume_adjustment_factor=old_face_value / new_face_value,
                ratio_numerator=old_face_value,
                ratio_denominator=new_face_value,
                note="Split ratio interpreted from old and new face values.",
            )

    return ParsedCorporateAction(
        symbol=record.symbol,
        action_type=CorporateActionType.UNSUPPORTED,
        ex_date=record.ex_date,
        record_date=record.record_date,
        purpose=record.purpose,
        price_adjustment_factor=ONE,
        volume_adjustment_factor=ONE,
        note="Unsupported corporate-action purpose; quarantine for manual review.",
    )


def factors_for_date(
    symbol: str,
    bar_date: date,
    actions: Iterable[ParsedCorporateAction],
) -> AdjustmentFactors:
    """Return cumulative backward-adjustment factors for one symbol and date."""

    clean_symbol = symbol.strip().upper()
    price_factor = ONE
    volume_factor = ONE

    for action in sorted(actions, key=lambda item: item.ex_date):
        if action.symbol != clean_symbol:
            continue
        if action.action_type == CorporateActionType.UNSUPPORTED:
            continue
        if bar_date >= action.ex_date:
            continue
        price_factor *= action.price_adjustment_factor
        volume_factor *= action.volume_adjustment_factor

    return AdjustmentFactors(price=price_factor, volume=volume_factor)


def _normalise_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _parse_ratio(value: str) -> tuple[Decimal, Decimal] | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*[:/]\s*(\d+(?:\.\d+)?)", value)
    if match is None:
        return None

    numerator = Decimal(match.group(1))
    denominator = Decimal(match.group(2))
    if numerator <= 0 or denominator <= 0:
        return None
    return numerator, denominator


def _parse_split_face_values(value: str) -> tuple[Decimal, Decimal] | None:
    money = r"(?:rs\.?|re\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:/-)?"
    match = re.search(rf"from\s+{money}\s+(?:to|into)\s+{money}", value)
    if match is None:
        return None

    old_face_value = Decimal(match.group(1))
    new_face_value = Decimal(match.group(2))
    if old_face_value <= 0 or new_face_value <= 0:
        return None
    return old_face_value, new_face_value
