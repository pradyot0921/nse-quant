# Three-Trade Hand Reconciliation V0

Date: 31 August 2026

This synthetic fixture validates the Phase 1 accounting path before any B001,
B002, or B003 result exists. It uses fixed bars, zero slippage, the frozen
Zerodha delivery cost profile, whole-share sizing, itemised trade-log rows,
daily NAV snapshots, an unfilled exit retry, and the round-trip turnover
counter.

No real strategy signal, real universe result, or benchmark return is used.

## Scenario

| Date | Event |
| --- | --- |
| 2026-01-05 | Signal wants `AAA`. |
| 2026-01-06 | Buy `AAA` at the next-session open. |
| 2026-01-06 | Signal exits all positions. |
| 2026-01-07 | `AAA` exit is explicitly untradeable; holding remains intact. |
| 2026-01-08 | Pending `AAA` exit retries and fills. |
| 2026-01-08 | Signal wants `BBB`. |
| 2026-01-09 | Buy `BBB`; affordability reduction sizes 10 reference shares down to 9. |

## Trade Reconciliation

| Date | Side | Symbol | Quantity | Price | Turnover | Cost | Cash After |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2026-01-06 | BUY | AAA | 11 | 90.00 | 990.00 | 1.19 | 8.81 |
| 2026-01-08 | SELL | AAA | 11 | 100.00 | 1100.00 | 16.38 | 1092.43 |
| 2026-01-09 | BUY | BBB | 9 | 109.24 | 983.16 | 1.19 | 108.08 |

The 2026-01-09 `BBB` entry would have been 10 shares from the reference cash
budget alone: `floor(1092.43 / 109.24) = 10`. Including costs makes 10 shares
unaffordable, so the sizing layer reduces the order to 9 shares.

## Cost Components

| Date | Side | Symbol | STT Buy | STT Sell | Exchange | SEBI | GST | Stamp | DP | Total |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-01-06 | BUY | AAA | 1.00 | 0.00 | 0.03 | 0.00 | 0.01 | 0.15 | 0.00 | 1.19 |
| 2026-01-08 | SELL | AAA | 0.00 | 1.00 | 0.03 | 0.00 | 0.01 | 0.00 | 15.34 | 16.38 |
| 2026-01-09 | BUY | BBB | 1.00 | 0.00 | 0.03 | 0.00 | 0.01 | 0.15 | 0.00 | 1.19 |

## Daily NAV

| Date | Cash | Holdings Value | NAV |
| --- | ---: | ---: | ---: |
| 2026-01-05 | 1000.00 | 0.00 | 1000.00 |
| 2026-01-06 | 8.81 | 1045.00 | 1053.81 |
| 2026-01-07 | 8.81 | 1067.00 | 1075.81 |
| 2026-01-08 | 1092.43 | 0.00 | 1092.43 |
| 2026-01-09 | 108.08 | 990.00 | 1098.08 |

## Turnover

The `AAA` buy and full sell complete one round trip in calendar year 2026.
Total executed turnover is:

`990.00 + 1100.00 + 983.16 = 3073.16`

## Interpretation

The test proves the current pre-B001 accounting path can reconcile a small run
from signal date through execution fills, itemised allocated costs, cash, daily
NAV, unfilled-exit retry, affordability resizing, and round-trip turnover.

It remains synthetic. It does not satisfy the later requirement to reconcile a
real broker contract note or funds statement.
