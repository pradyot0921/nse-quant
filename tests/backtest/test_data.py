from datetime import date
from decimal import Decimal
import csv

import pytest

from nse_quant.backtest.data import (
    BacktestDataError,
    group_bars_by_date,
    load_processed_backtest_bars,
)


FIELDNAMES = [
    "trade_date",
    "symbol",
    "adjusted_open",
    "adjusted_high",
    "adjusted_low",
    "adjusted_close",
    "adjusted_volume",
    "raw_traded_value",
]


def row(**overrides):
    values = {
        "trade_date": "2026-08-19",
        "symbol": "ABC",
        "adjusted_open": "100.000000",
        "adjusted_high": "110.000000",
        "adjusted_low": "90.000000",
        "adjusted_close": "105.000000",
        "adjusted_volume": "1000.000000",
        "raw_traded_value": "105000.00",
    }
    values.update(overrides)
    return values


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def test_load_processed_backtest_bars_sorts_and_converts_decimal_prices(tmp_path):
    path = tmp_path / "processed.csv"
    write_csv(
        path,
        [
            row(symbol="XYZ"),
            row(symbol="ABC", trade_date="2026-08-18"),
        ],
    )

    bars = load_processed_backtest_bars(path)

    assert [(bar.trade_date, bar.symbol) for bar in bars] == [
        (date(2026, 8, 18), "ABC"),
        (date(2026, 8, 19), "XYZ"),
    ]
    assert bars[0].adjusted_close == Decimal("105.000000")


def test_group_bars_by_date_returns_daily_symbol_lookup(tmp_path):
    path = tmp_path / "processed.csv"
    write_csv(path, [row(symbol="XYZ"), row(symbol="ABC")])

    daily = group_bars_by_date(load_processed_backtest_bars(path))

    assert len(daily) == 1
    assert [bar.symbol for bar in daily[0].bars] == ["ABC", "XYZ"]
    assert daily[0].require("xyz").symbol == "XYZ"


def test_load_processed_backtest_bars_rejects_duplicates_and_bad_prices(tmp_path):
    duplicate = tmp_path / "duplicate.csv"
    write_csv(duplicate, [row(), row()])

    with pytest.raises(BacktestDataError, match="duplicate"):
        load_processed_backtest_bars(duplicate)

    bad_price = tmp_path / "bad_price.csv"
    write_csv(bad_price, [row(adjusted_close="0")])

    with pytest.raises(BacktestDataError, match="adjusted_close must be positive"):
        load_processed_backtest_bars(bad_price)
