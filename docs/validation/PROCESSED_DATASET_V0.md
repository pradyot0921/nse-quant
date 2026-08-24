# Processed Dataset Build V0

**Status:** Evidence artifact

## Summary

| Metric | Value |
| --- | ---: |
| Dataset version | `nifty100_v0_adjusted_ohlcv_d039` |
| Frozen universe symbols | 20 |
| Ordinary sessions | 2618 |
| Processed bars | 52360 |
| Bars with non-unit price factor | 12030 |
| Corporate actions parsed for selected symbols | 362 |
| Market-data missing files | 0 |
| Market-data file failures | 0 |
| Market-data row rejections | 0 |
| Processed CSV | `data/processed/nifty100_v0_adjusted_ohlcv.csv` |
| Processed CSV SHA-256 | `74f25a13116f5658201870ee6ae7c35ac5d27153ccbf3b65909e078355f75b4e` |

## Source Formats

| Source | Bars |
| --- | ---: |
| NSE_CM_UDIFF | 10440 |
| NSE_LEGACY_CM_BHAVCOPY | 41920 |

## Corporate Actions

| Type | Count |
| --- | ---: |
| SPLIT | 3 |
| BONUS | 11 |
| IGNORED | 348 |
| UNSUPPORTED | 0 |

## Supported Adjustments Applied

| Symbol | Ex-Date | Type | Purpose | Price Factor | Volume Factor |
| --- | --- | --- | --- | ---: | ---: |
| BAJAJFINSV | 2022-09-13 | BONUS | Bonus 1:1 | 0.5000000000 | 2.0000000000 |
| BAJAJFINSV | 2022-09-13 | SPLIT | Face Value Split (Sub-Division) - From Rs 5/- Per Share To Re 1/- Per Share | 0.2000000000 | 5.0000000000 |
| BPCL | 2016-07-13 | BONUS | Bonus 1:1 | 0.5000000000 | 2.0000000000 |
| BPCL | 2017-07-13 | BONUS | Bonus 1:2 | 0.6666666667 | 1.5000000000 |
| BPCL | 2024-06-21 | BONUS | Bonus 1:1 | 0.5000000000 | 2.0000000000 |
| HCLTECH | 2019-12-05 | BONUS | Bonus 1:1 | 0.5000000000 | 2.0000000000 |
| HDFCBANK | 2019-09-19 | SPLIT | Face Value Split (Sub-Division) - From Rs 2 Per Share To Rs 1 Per Share | 0.5000000000 | 2.0000000000 |
| HDFCBANK | 2025-08-26 | BONUS | Bonus 1:1 | 0.5000000000 | 2.0000000000 |
| ICICIBANK | 2017-06-20 | BONUS | Annual General Meeting/Dividend - Rs 2.50 Per Share/Bonus 1:10 (Revised) | 0.9090909091 | 1.1000000000 |
| INFY | 2018-09-04 | BONUS | Bonus 1:1 | 0.5000000000 | 2.0000000000 |
| KOTAKBANK | 2026-01-14 | SPLIT | Face Value Split (Sub-Division) - From Rs 5/- Per Share To Re 1/- Per Share | 0.2000000000 | 5.0000000000 |
| LT | 2017-07-13 | BONUS | Bonus 1:2 | 0.6666666667 | 1.5000000000 |
| M&M | 2017-12-21 | BONUS | Bonus 1:1 | 0.5000000000 | 2.0000000000 |
| TCS | 2018-05-31 | BONUS | Bonus 1:1 /Dividend- Rs 29 Per Share | 0.5000000000 | 2.0000000000 |

## Rows Per Symbol

| Symbol | Rows |
| --- | ---: |
| ICICIBANK | 2618 |
| SBIN | 2618 |
| HDFCBANK | 2618 |
| INFY | 2618 |
| AXISBANK | 2618 |
| TCS | 2618 |
| MARUTI | 2618 |
| KOTAKBANK | 2618 |
| LT | 2618 |
| SUNPHARMA | 2618 |
| HINDALCO | 2618 |
| HCLTECH | 2618 |
| M&M | 2618 |
| TITAN | 2618 |
| TECHM | 2618 |
| BANKBARODA | 2618 |
| ASIANPAINT | 2618 |
| JINDALSTEL | 2618 |
| BAJAJFINSV | 2618 |
| BPCL | 2618 |

## Interpretation

This report records a reproducible local processed-dataset build for the
already frozen V0 universe. The processed CSV is deliberately not tracked
in git; the committed evidence is this manifest, including row counts,
corporate-action adjustments, and a content hash.
