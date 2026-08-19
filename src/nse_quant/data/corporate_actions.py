"""Corporate-action parsing and adjustment factors.

Phase 1 intentionally supports only deterministic splits and bonuses. Other
NSE corporate-action purpose strings are returned as unsupported so ingestion
can quarantine them instead of guessing from free text.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import re
from typing import Iterable


ONE = Decimal("1")
ADJUSTMENT_FACTOR = Decimal("0.0000000001")


class CorporateActionType(str, Enum):
    SPLIT = "split"
    BONUS = "bonus"
    IGNORED = "ignored"
    UNSUPPORTED = "unsupported"


class UnsupportedCorporateActionError(RuntimeError):
    """Raised when adjustment factors are requested for quarantined actions."""


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
    has_bonus = "bonus" in purpose
    has_split = _has_split_token(purpose)

    if has_bonus and has_split:
        return _unsupported(
            record,
            "Combined split and bonus action requires multi-event support; quarantine for manual review.",
        )

    if has_bonus:
        if _has_unsupported_bonus_instrument(purpose):
            return _unsupported(
                record,
                "Bonus instrument is not an equity-share bonus issue; quarantine for manual review.",
            )

        ratio = _parse_bonus_ratio(purpose)
        if ratio is not None:
            new_shares, old_shares = ratio
            share_factor = (old_shares + new_shares) / old_shares
            return ParsedCorporateAction(
                symbol=record.symbol,
                action_type=CorporateActionType.BONUS,
                ex_date=record.ex_date,
                record_date=record.record_date,
                purpose=record.purpose,
                price_adjustment_factor=_factor(
                    old_shares / (old_shares + new_shares)
                ),
                volume_adjustment_factor=_factor(share_factor),
                ratio_numerator=new_shares,
                ratio_denominator=old_shares,
                note="Bonus ratio interpreted as new shares per existing shares.",
            )

        return _unsupported(
            record,
            "Bonus action ratio could not be parsed safely; quarantine for manual review.",
        )

    if has_split:
        face_values = _parse_split_face_values(purpose)
        if face_values is not None:
            old_face_value, new_face_value = face_values
            return ParsedCorporateAction(
                symbol=record.symbol,
                action_type=CorporateActionType.SPLIT,
                ex_date=record.ex_date,
                record_date=record.record_date,
                purpose=record.purpose,
                price_adjustment_factor=_factor(new_face_value / old_face_value),
                volume_adjustment_factor=_factor(old_face_value / new_face_value),
                ratio_numerator=old_face_value,
                ratio_denominator=new_face_value,
                note="Split ratio interpreted from old and new face values.",
            )

        return _unsupported(
            record,
            "Split action face-value change could not be parsed safely; quarantine for manual review.",
        )

    if _has_ignored_noop_event(purpose):
        return _ignored(
            record,
            "Recognised no-price-adjustment event; ignored for V1 adjusted OHLCV.",
        )

    return _unsupported(
        record,
        "Unsupported corporate-action purpose; quarantine for manual review.",
    )


def _ignored(record: CorporateActionRecord, note: str) -> ParsedCorporateAction:
    return ParsedCorporateAction(
        symbol=record.symbol,
        action_type=CorporateActionType.IGNORED,
        ex_date=record.ex_date,
        record_date=record.record_date,
        purpose=record.purpose,
        price_adjustment_factor=ONE,
        volume_adjustment_factor=ONE,
        note=note,
    )


def _unsupported(record: CorporateActionRecord, note: str) -> ParsedCorporateAction:
    return ParsedCorporateAction(
        symbol=record.symbol,
        action_type=CorporateActionType.UNSUPPORTED,
        ex_date=record.ex_date,
        record_date=record.record_date,
        purpose=record.purpose,
        price_adjustment_factor=ONE,
        volume_adjustment_factor=ONE,
        note=note,
    )


def validate_actions(
    symbols: Iterable[str],
    actions: Iterable[ParsedCorporateAction],
    *,
    start_date: date | None = None,
    end_date: date | None = None,
) -> None:
    """Raise if quarantined actions affect the requested symbols and date range."""

    clean_symbols = {symbol.strip().upper() for symbol in symbols}
    for action in actions:
        if action.symbol not in clean_symbols:
            continue
        if start_date is not None and action.ex_date < start_date:
            continue
        if end_date is not None and action.ex_date > end_date:
            continue
        if action.action_type == CorporateActionType.UNSUPPORTED:
            raise UnsupportedCorporateActionError(
                f"{action.symbol}: unsupported corporate action on "
                f"{action.ex_date}: {action.purpose}"
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
        if action.action_type in {
            CorporateActionType.IGNORED,
            CorporateActionType.UNSUPPORTED,
        }:
            continue
        if bar_date >= action.ex_date:
            continue
        price_factor = _factor(price_factor * action.price_adjustment_factor)
        volume_factor = _factor(volume_factor * action.volume_adjustment_factor)

    return AdjustmentFactors(price=price_factor, volume=volume_factor)


def _normalise_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _factor(amount: Decimal) -> Decimal:
    return amount.quantize(ADJUSTMENT_FACTOR, rounding=ROUND_HALF_UP)


def _has_split_token(value: str) -> bool:
    return "split" in value or "sub-division" in value or "sub division" in value


def _has_unsupported_bonus_instrument(value: str) -> bool:
    return re.search(r"\bbonus\s+(?:debentures?|preference)\b", value) is not None


def _has_ignored_noop_event(value: str) -> bool:
    ignored_patterns = [
        r"\bdividend\b",
        r"\bagm\b",
        r"\begm\b",
        r"\bannual general meeting\b",
        r"\bextraordinary general meeting\b",
        r"\bboard meeting\b",
        r"\bchange(?:d)? in name\b",
        r"\bname change\b",
    ]
    return any(re.search(pattern, value) is not None for pattern in ignored_patterns)


def _parse_bonus_ratio(value: str) -> tuple[Decimal, Decimal] | None:
    matches = list(
        re.finditer(
            r"(?<![\d.])(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)(?![\d.])",
            value,
        )
    )
    if len(matches) != 1:
        return None

    match = matches[0]
    context_start = max(0, match.start() - 40)
    context_end = min(len(value), match.end() + 40)
    context = value[context_start:context_end]
    if "bonus" not in context and "ratio" not in context:
        return None

    numerator = Decimal(match.group(1))
    denominator = Decimal(match.group(2))
    if numerator <= 0 or denominator <= 0:
        return None
    if denominator > Decimal("20"):
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
