# Historical Source Bridge V0

**Date:** 23 August 2026
**Status:** Pre-implementation source decision

## Purpose

D-030 fixes the V0 data-audit window as 1 January 2016 through
19 August 2026. The existing CM-UDiFF parser covers the modern NSE common
bhavcopy format, but the project still needs a deterministic source bridge for
the pre-UDiFF part of that window.

This note records the source split before any full-window download, universe
selection, or B001/B002/B003 result exists.

## Source Split

| Date range | Source family | Raw storage |
| --- | --- | --- |
| 2016-01-01 through 2024-07-05 | NSE `Full Bhavcopy and Security Deliverable data` | `data/raw/nse/cm_full_bhavcopy/YYYY/MM/` |
| 2024-07-08 through 2026-08-19 | NSE `CM-UDiFF Common Bhavcopy Final` | `data/raw/nse/cm_udiff/YYYY/MM/` |

6 July 2024 and 7 July 2024 were a Saturday/Sunday boundary between the two
source families. If the checked-in calendar later identifies either date as a
special cash-market session, that date must be handled by an explicit source
note before dataset construction.

## Rationale

NSE's All Reports page identifies `CM-UDiFF Common Bhavcopy Final (zip)` as the
current CM bhavcopy source. The same page states that the older `CM -
Bhavcopy(csv)` and `CM - Common Bhavcopy (csv)` reports were discontinued with
effect from 8 July 2024 and directs users to CM-UDiFF.

The same official reports page lists `Full Bhavcopy and Security Deliverable
data`. V0 selects that official NSE report as the pre-UDiFF bridge because it
contains daily cash-equity OHLCV-style data and delivery/traded-value fields
that are useful for liquidity and data-quality validation.

## Canonical Normalized Fields

Both source families must normalize into one canonical daily-bar schema before
corporate-action adjustment or universe selection:

```text
trade_date
source_format
symbol
isin
series
previous_close
open
high
low
close
last
raw_traded_volume
raw_traded_value
trades_count
delivery_quantity
delivery_percent
source_file
```

`isin`, `trades_count`, `delivery_quantity`, and `delivery_percent` may be
nullable only when the source format genuinely lacks the field. Missing fields
must be explicit in the processed manifest rather than silently filled.

## Provisional Legacy Mapping

The expected legacy full-bhavcopy mapping must be confirmed against real files
before parser implementation:

| Canonical field | Expected legacy field |
| --- | --- |
| `trade_date` | `DATE1` |
| `symbol` | `SYMBOL` |
| `series` | `SERIES` |
| `previous_close` | `PREV_CLOSE` |
| `open` | `OPEN_PRICE` |
| `high` | `HIGH_PRICE` |
| `low` | `LOW_PRICE` |
| `close` | `CLOSE_PRICE` |
| `last` | `LAST_PRICE` |
| `raw_traded_volume` | `TTL_TRD_QNTY` |
| `raw_traded_value` | `TURNOVER_LACS * 100000` |
| `trades_count` | `NO_OF_TRADES` |
| `delivery_quantity` | `DELIV_QTY` |
| `delivery_percent` | `DELIV_PER` |

Do not implement from this table alone. It is a hypothesis to validate against
real NSE files.

## Validation Required Before Parser Implementation

Before writing the legacy parser, inspect real files from at least:

- one early-window date in 2016;
- one pre-COVID normal date in 2019;
- one March 2020 stress-period date;
- one post-COVID date in 2022;
- one final legacy-era date near 5 July 2024.

For each file, record:

- filename and source URL or report provenance;
- raw header exactly as shipped;
- total rows and `EQ` rows;
- all distinct `SERIES` values with counts;
- whether the date column matches the file date;
- whether duplicate `SYMBOL` values exist inside `EQ`;
- zero or non-positive OHLC, volume, traded value, or trade-count rows;
- whether `TURNOVER_LACS * 100000 / TTL_TRD_QNTY` lies within the daily
  low/high range after the same tolerance logic used for UDiFF.

If the legacy files differ across years, record a versioned schema split rather
than widening a single parser until it accepts everything.

## Validation Consequences

The legacy source is expected to lack ISIN. The D-019 ISIN-continuity guard
therefore applies only when normalized rows contain ISIN. Pre-UDiFF
corporate-action safety depends on:

- the full-window NSE corporate-action scan;
- unsupported-action exclusion before universe freeze;
- raw-versus-adjusted continuity checks around real split/bonus events;
- explicit quarantine of unexplained discontinuities discovered by validation.

This is weaker than an independent ISIN-change signal, so the processed dataset
manifest must label the pre-UDiFF segment as:

```text
IDENTIFIER_CONTINUITY_CHECK: NOT AVAILABLE BEFORE 2024-07-08
```

## Next Work

1. Create the legacy source-format scan artifact.
2. Implement a separate legacy parser module.
3. Normalize legacy and UDiFF rows into the same canonical schema.
4. Build the full-window checked-in calendar.
5. Run full-window acquisition and row-quality scans.
