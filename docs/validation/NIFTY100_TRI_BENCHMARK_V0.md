# Nifty 100 TRI Benchmark Data V0

**Status:** Evidence artifact

## Source

Official source: `https://www.niftyindices.com/reports/historical-data`
Report: `Total returns Index Values`
Index: `NIFTY 100`

## Summary

| Metric | Count |
| --- | ---: |
| Benchmark rows | 2634 |
| Sessions checked | 2618 |
| Missing benchmark dates | 0 |
| Extra benchmark dates | 16 |

## Date Range

First benchmark row: `2016-01-01`
Last benchmark row: `2026-08-19`


## Missing Benchmark Dates

None.

## Extra Benchmark Dates

| Date |
| --- |
| 2016-10-30 |
| 2017-10-19 |
| 2018-11-07 |
| 2019-10-27 |
| 2020-02-01 |
| 2020-11-14 |
| 2021-11-04 |
| 2022-10-24 |
| 2023-11-12 |
| 2024-01-20 |
| 2024-03-02 |
| 2024-05-18 |
| 2024-11-01 |
| 2025-02-01 |
| 2025-10-21 |
| 2026-02-01 |

## Interpretation

The official TRI series is the benchmark for Phase 1. Missing benchmark
dates are blocking because strategy NAV and benchmark drawdown must be
computed over the identical evaluation period.

Extra benchmark dates are reported for audit. They are not blocking
by themselves when they correspond to special sessions excluded from
default V0 research bars under D-029.
