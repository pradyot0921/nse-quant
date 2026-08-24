# Legacy CM Bhavcopy / CM-UDiFF Seam Validation V0

**Date:** 24 August 2026  
**Status:** Evidence artifact

## Scope

Checked NSE sessions from `2024-07-01` through `2024-07-12` around the 8 July 2024 UDiFF transition.

Raw root used: `data\raw`
Delay seconds: `0.0`
Max retries: `0`
Timeout seconds: `20.0`

## Source Availability

| Source | Available | Missing | Failed |
| --- | ---: | ---: | ---: |
| Legacy CM bhavcopy | 5 | 5 | 0 |
| CM-UDiFF | 10 | 0 | 0 |

## Per-Date Results

| Date | Legacy status | Legacy EQ rows | UDiFF status | UDiFF EQ rows |
| --- | --- | ---: | --- | ---: |
| 2024-07-01 | available | 1914 | available | 1914 |
| 2024-07-02 | available | 1914 | available | 1914 |
| 2024-07-03 | available | 1911 | available | 1911 |
| 2024-07-04 | available | 1910 | available | 1910 |
| 2024-07-05 | available | 1906 | available | 1906 |
| 2024-07-08 | missing | 0 | available | 1909 |
| 2024-07-09 | missing | 0 | available | 1909 |
| 2024-07-10 | missing | 0 | available | 1913 |
| 2024-07-11 | missing | 0 | available | 1909 |
| 2024-07-12 | missing | 0 | available | 1907 |

## Same-Date Overlap Comparison

| Date | Legacy rows | UDiFF rows | Common symbols | Legacy-only | UDiFF-only | Mismatches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024-07-01 | 1914 | 1914 | 1914 | 0 | 0 | 0 |
| 2024-07-02 | 1914 | 1914 | 1914 | 0 | 0 | 0 |
| 2024-07-03 | 1911 | 1911 | 1911 | 0 | 0 | 0 |
| 2024-07-04 | 1910 | 1910 | 1910 | 0 | 0 | 0 |
| 2024-07-05 | 1906 | 1906 | 1906 | 0 | 0 | 0 |

## Boundary Previous-Close Check

| Legacy date | UDiFF date | Common symbols | Legacy-only | UDiFF-only | Previous-close mismatches |
| --- | --- | ---: | ---: | ---: | ---: |
| 2024-07-05 | 2024-07-08 | 1903 | 3 | 6 | 0 |

No previous-close mismatches observed for common symbols.

## Failures

None.

## Interpretation

Same-date source overlap was observed on 5 sessions.
For those overlap sessions, the legacy CM bhavcopy parser and CM-UDiFF
parser produced identical canonical EQ rows for every common symbol.

The first V0 CM-UDiFF session also passed the boundary check: for common
symbols, 8 July 2024 UDiff `previous_close` matched 5 July 2024 legacy
CM bhavcopy `close` exactly.

This validates the July 2024 source-family bridge for the canonical fields
used by Phase 1 daily bars: symbol, ISIN, series, OHLC, previous close,
last price, traded volume, traded value, and transaction count.

Raw archives remain outside version control; this report records the
source-family availability and comparison results needed before processed
dataset construction.
