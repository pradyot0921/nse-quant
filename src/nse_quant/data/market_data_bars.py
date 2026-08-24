"""Canonical daily equity bars shared by NSE market-data source families."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from nse_quant.data.nse_legacy_bhavcopy import LegacyBhavcopyEquityBar
from nse_quant.data.nse_udiff import UDiffEquityBar


SOURCE_LEGACY_CM_BHAVCOPY = "NSE_LEGACY_CM_BHAVCOPY"
SOURCE_CM_UDIFF = "NSE_CM_UDIFF"


@dataclass(frozen=True)
class CanonicalEquityBar:
    trade_date: date
    source_format: str
    symbol: str
    isin: str
    series: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    previous_close: Decimal
    last_price: Decimal
    volume: int
    traded_value: Decimal
    transaction_count: int


def canonical_bar_from_legacy(bar: LegacyBhavcopyEquityBar) -> CanonicalEquityBar:
    """Normalize one legacy CM bhavcopy equity bar."""

    return CanonicalEquityBar(
        trade_date=bar.trade_date,
        source_format=SOURCE_LEGACY_CM_BHAVCOPY,
        symbol=bar.symbol,
        isin=bar.isin,
        series=bar.series,
        open=bar.open,
        high=bar.high,
        low=bar.low,
        close=bar.close,
        previous_close=bar.previous_close,
        last_price=bar.last_price,
        volume=bar.volume,
        traded_value=bar.traded_value,
        transaction_count=bar.transaction_count,
    )


def canonical_bar_from_udiff(bar: UDiffEquityBar) -> CanonicalEquityBar:
    """Normalize one CM-UDiFF equity bar."""

    return CanonicalEquityBar(
        trade_date=bar.trade_date,
        source_format=SOURCE_CM_UDIFF,
        symbol=bar.symbol,
        isin=bar.isin,
        series=bar.series,
        open=bar.open,
        high=bar.high,
        low=bar.low,
        close=bar.close,
        previous_close=bar.previous_close,
        last_price=bar.last_price,
        volume=bar.volume,
        traded_value=bar.traded_value,
        transaction_count=bar.transaction_count,
    )


def comparable_bar_values(bar: CanonicalEquityBar) -> tuple[object, ...]:
    """Return source-independent fields for same-date parser comparison."""

    return (
        bar.trade_date,
        bar.symbol,
        bar.isin,
        bar.series,
        bar.open,
        bar.high,
        bar.low,
        bar.close,
        bar.previous_close,
        bar.last_price,
        bar.volume,
        bar.traded_value,
        bar.transaction_count,
    )
