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
ADJUSTED_PRICE = Decimal("0.000001")
ADJUSTED_VOLUME = Decimal("0.000001")


class CorporateActionType(str, Enum):
    SPLIT = "split"
    BONUS = "bonus"
    IGNORED = "ignored"
    UNSUPPORTED = "unsupported"


class UnsupportedCorporateActionError(RuntimeError):
    """Raised when adjustment factors are requested for quarantined actions."""


class MissingCorporateActionError(RuntimeError):
    """Raised when price data implies an unrecorded corporate action."""


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


@dataclass(frozen=True)
class OHLCVBar:
    symbol: str
    bar_date: date
    open: Decimal | str | int
    high: Decimal | str | int
    low: Decimal | str | int
    close: Decimal | str | int
    volume: Decimal | str | int
    isin: str | None = None

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol is required")
        symbol = self.symbol.strip().upper()
        prices = {
            "open": _to_decimal(self.open, field_name="open"),
            "high": _to_decimal(self.high, field_name="high"),
            "low": _to_decimal(self.low, field_name="low"),
            "close": _to_decimal(self.close, field_name="close"),
        }
        for field_name, value in prices.items():
            if value <= 0:
                raise ValueError(f"{field_name} must be positive")
        volume = _to_decimal(self.volume, field_name="volume")
        if volume < 0:
            raise ValueError("volume must be non-negative")

        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "open", prices["open"])
        object.__setattr__(self, "high", prices["high"])
        object.__setattr__(self, "low", prices["low"])
        object.__setattr__(self, "close", prices["close"])
        object.__setattr__(self, "volume", volume)
        if self.isin is not None:
            object.__setattr__(self, "isin", self.isin.strip().upper() or None)


@dataclass(frozen=True)
class AdjustedOHLCVBar:
    symbol: str
    bar_date: date
    isin: str | None
    raw_open: Decimal
    raw_high: Decimal
    raw_low: Decimal
    raw_close: Decimal
    raw_volume: Decimal
    adjusted_open: Decimal
    adjusted_high: Decimal
    adjusted_low: Decimal
    adjusted_close: Decimal
    adjusted_volume: Decimal
    price_factor: Decimal
    volume_factor: Decimal


def parse_corporate_action(record: CorporateActionRecord) -> ParsedCorporateAction:
    """Parse one NSE corporate-action record into deterministic adjustment factors."""

    purpose = _normalise_text(record.purpose)
    has_bonus = "bonus" in purpose
    has_split = _has_split_token(purpose)

    if "scheme of arrangement" in purpose:
        return _unsupported(
            record,
            "Scheme of arrangement requires corporate-reorganisation support; quarantine for manual review.",
        )

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


def validate_rights_exclusions(
    symbols: Iterable[str],
    actions: Iterable[ParsedCorporateAction],
    *,
    start_date: date | None = None,
    end_date: date | None = None,
) -> None:
    """Raise if V0 universe candidates have rights issues in the research window.

    This is a universe-selection guard. The OHLCV adjustment path does not call
    it because rights issues already halt there as unsupported actions.
    """

    clean_symbols = {symbol.strip().upper() for symbol in symbols}
    for action in actions:
        if action.symbol not in clean_symbols:
            continue
        if start_date is not None and action.ex_date < start_date:
            continue
        if end_date is not None and action.ex_date > end_date:
            continue
        if "rights" in _normalise_text(action.purpose):
            raise UnsupportedCorporateActionError(
                f"{action.symbol}: rights issue in V0 research window on "
                f"{action.ex_date}: {action.purpose}"
            )


def validate_isin_continuity(
    bars: Iterable[OHLCVBar],
    actions: Iterable[ParsedCorporateAction],
) -> None:
    """Raise when an ISIN change has no same-date corporate-action record."""

    action_index = {(action.symbol, action.ex_date) for action in actions}
    previous_by_symbol: dict[str, OHLCVBar] = {}
    for bar in sorted(bars, key=lambda item: (item.symbol, item.bar_date)):
        previous = previous_by_symbol.get(bar.symbol)
        if (
            previous is not None
            and previous.isin is not None
            and bar.isin is not None
            and previous.isin != bar.isin
            and (bar.symbol, bar.bar_date) not in action_index
        ):
            raise MissingCorporateActionError(
                f"{bar.symbol}: ISIN changed from {previous.isin} to "
                f"{bar.isin} on {bar.bar_date} without a same-date corporate action"
            )
        previous_by_symbol[bar.symbol] = bar


def adjust_ohlcv_bars(
    bars: Iterable[OHLCVBar],
    actions: Iterable[ParsedCorporateAction],
) -> tuple[AdjustedOHLCVBar, ...]:
    """Apply backward-adjustment factors to raw OHLCV bars."""

    clean_bars = tuple(bars)
    clean_actions = tuple(actions)
    validate_actions({bar.symbol for bar in clean_bars}, clean_actions)
    validate_isin_continuity(clean_bars, clean_actions)

    adjusted = []
    for bar in clean_bars:
        factors = factors_for_date(bar.symbol, bar.bar_date, clean_actions)
        adjusted.append(
            AdjustedOHLCVBar(
                symbol=bar.symbol,
                bar_date=bar.bar_date,
                isin=bar.isin,
                raw_open=bar.open,
                raw_high=bar.high,
                raw_low=bar.low,
                raw_close=bar.close,
                raw_volume=bar.volume,
                adjusted_open=_adjust_price(bar.open, factors.price),
                adjusted_high=_adjust_price(bar.high, factors.price),
                adjusted_low=_adjust_price(bar.low, factors.price),
                adjusted_close=_adjust_price(bar.close, factors.price),
                adjusted_volume=_adjust_volume(bar.volume, factors.volume),
                price_factor=factors.price,
                volume_factor=factors.volume,
            )
        )

    return tuple(adjusted)


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
    unsupported_instruments = [
        r"debentures?",
        r"preference",
        r"ncrps",
        r"ncds?",
        r"crps",
        r"ocrps",
        r"warrants?",
    ]
    if re.search(rf"\bbonus\s+(?:{'|'.join(unsupported_instruments)})\b", value):
        return True

    match = re.search(r"\bbonus\b\s*([a-z0-9:./-]+)?", value)
    if match is None:
        return False
    next_token = match.group(1)
    if next_token is None:
        return False
    if re.fullmatch(r"\d+(?:\.\d+)?:\d+(?:\.\d+)?", next_token):
        return False
    return next_token not in {"issue", "shares", "share", "equity", "ratio", "record"}


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
        r"\bbuy back\b",
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
    per_share = r"(?:\s+per\s+share)?"
    match = re.search(rf"from\s+{money}{per_share}\s+(?:to|into)\s+{money}{per_share}", value)
    if match is None:
        return None

    old_face_value = Decimal(match.group(1))
    new_face_value = Decimal(match.group(2))
    if old_face_value <= 0 or new_face_value <= 0:
        return None
    return old_face_value, new_face_value


def _to_decimal(value: Decimal | str | int, *, field_name: str) -> Decimal:
    if isinstance(value, float):
        raise TypeError(f"{field_name} must not be a binary float")
    return Decimal(value)


def _adjust_price(value: Decimal, factor: Decimal) -> Decimal:
    return (value * factor).quantize(ADJUSTED_PRICE, rounding=ROUND_HALF_UP)


def _adjust_volume(value: Decimal, factor: Decimal) -> Decimal:
    return (value * factor).quantize(ADJUSTED_VOLUME, rounding=ROUND_HALF_UP)
