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
| 2016-01-01 through 2024-07-05 | NSE `CM - Bhavcopy(csv)` historical ZIP | `data/raw/nse/cm_bhavcopy/YYYY/MM/` |
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

This initial note selected `Full Bhavcopy and Security Deliverable data` as the
pre-UDiFF bridge. D-032 supersedes that choice after real-file validation:
`sec_bhavdata_full_DDMMYYYY.csv` returned 404 for tested 2016 and 2019 dates,
while the older CM bhavcopy ZIP covered the full sampled legacy window and
included ISIN plus raw traded value in rupees.

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
source_file
```

`isin` and `trades_count` may be nullable only when the source format genuinely
lacks the field. Missing fields must be explicit in the processed manifest
rather than silently filled. Delivery quantity and delivery percentage are not
present in the selected legacy CM bhavcopy ZIP source.

## Legacy Mapping

The selected legacy CM bhavcopy ZIP mapping is:

| Canonical field | Expected legacy field |
| --- | --- |
| `trade_date` | `TIMESTAMP` |
| `symbol` | `SYMBOL` |
| `isin` | `ISIN` |
| `series` | `SERIES` |
| `previous_close` | `PREVCLOSE` |
| `open` | `OPEN` |
| `high` | `HIGH` |
| `low` | `LOW` |
| `close` | `CLOSE` |
| `last` | `LAST` |
| `raw_traded_volume` | `TOTTRDQTY` |
| `raw_traded_value` | `TOTTRDVAL` |
| `trades_count` | `TOTALTRADES` |

This mapping is backed by `docs/validation/LEGACY_CM_BHAVCOPY_FORMAT_SCAN_V0.md`.

## Validation Required Before Parser Implementation

The legacy scan inspected real files from:

- 4 January 2016;
- 3 June 2019;
- 23 March 2020;
- 1 August 2022;
- 5 July 2024.

For each file, the artifact records filename/source URL, raw header, total and
EQ rows, all distinct `SERIES` counts, date-column agreement, duplicate EQ
symbol checks, zero/non-positive OHLC/activity checks, and the traded-value
VWAP range invariant.

If the legacy files differ across years, record a versioned schema split rather
than widening a single parser until it accepts everything.

## Validation Consequences

The selected legacy source includes ISIN. The D-019 ISIN-continuity guard
therefore applies to the pre-UDiFF segment once normalized rows are available.
Corporate-action safety also depends on:

- the full-window NSE corporate-action scan;
- unsupported-action exclusion before universe freeze;
- raw-versus-adjusted continuity checks around real split/bonus events;
- explicit quarantine of unexplained discontinuities discovered by validation.

## Next Work

1. Implement a separate legacy CM bhavcopy parser module.
2. Normalize legacy and UDiFF rows into the same canonical schema.
3. Build the full-window checked-in calendar.
4. Run full-window acquisition and row-quality scans.
