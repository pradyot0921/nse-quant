from datetime import date
from decimal import Decimal

from nse_quant.data.market_data_bars import (
    SOURCE_CM_UDIFF,
    SOURCE_LEGACY_CM_BHAVCOPY,
    canonical_bar_from_legacy,
    canonical_bar_from_udiff,
    comparable_bar_values,
)
from nse_quant.data.nse_legacy_bhavcopy import LegacyBhavcopyEquityBar
from nse_quant.data.nse_udiff import UDiffEquityBar


def legacy_bar(**overrides):
    values = {
        "trade_date": date(2024, 7, 5),
        "source_format": "legacy parser source",
        "symbol": "BEML",
        "isin": "INE258A01016",
        "series": "EQ",
        "open": Decimal("4453.70"),
        "high": Decimal("4505.00"),
        "low": Decimal("4382.90"),
        "close": Decimal("4399.80"),
        "previous_close": Decimal("4410.00"),
        "last_price": Decimal("4400.00"),
        "volume": 349959,
        "traded_value": Decimal("1554003341.40"),
        "transaction_count": 16988,
    }
    values.update(overrides)
    return LegacyBhavcopyEquityBar(**values)


def udiff_bar(**overrides):
    values = {
        "trade_date": date(2024, 7, 5),
        "business_date": date(2024, 7, 5),
        "symbol": "BEML",
        "isin": "INE258A01016",
        "series": "EQ",
        "instrument_type": "STK",
        "instrument_id": "200",
        "open": Decimal("4453.70"),
        "high": Decimal("4505.00"),
        "low": Decimal("4382.90"),
        "close": Decimal("4399.80"),
        "previous_close": Decimal("4410.00"),
        "last_price": Decimal("4400.00"),
        "volume": 349959,
        "traded_value": Decimal("1554003341.40"),
        "transaction_count": 16988,
        "session_id": "F1",
    }
    values.update(overrides)
    return UDiffEquityBar(**values)


def test_canonical_bar_from_legacy_maps_research_fields():
    canonical = canonical_bar_from_legacy(legacy_bar())

    assert canonical.source_format == SOURCE_LEGACY_CM_BHAVCOPY
    assert canonical.symbol == "BEML"
    assert canonical.isin == "INE258A01016"
    assert canonical.open == Decimal("4453.70")
    assert canonical.previous_close == Decimal("4410.00")
    assert canonical.traded_value == Decimal("1554003341.40")


def test_canonical_bar_from_udiff_maps_matching_research_fields():
    canonical = canonical_bar_from_udiff(udiff_bar())

    assert canonical.source_format == SOURCE_CM_UDIFF
    assert canonical.symbol == "BEML"
    assert canonical.isin == "INE258A01016"
    assert canonical.open == Decimal("4453.70")
    assert canonical.previous_close == Decimal("4410.00")
    assert canonical.traded_value == Decimal("1554003341.40")


def test_comparable_bar_values_ignore_source_format():
    legacy = canonical_bar_from_legacy(legacy_bar())
    udiff = canonical_bar_from_udiff(udiff_bar())

    assert legacy.source_format != udiff.source_format
    assert comparable_bar_values(legacy) == comparable_bar_values(udiff)
