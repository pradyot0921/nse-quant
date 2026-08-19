# NSE CM Session Calendar V0

**Date:** 20 August 2026
**Status:** Accepted as one-year calendar/acquisition evidence

## Source

The checked-in session calendar covers 20 August 2025 through 19 August 2026.

Normal sessions were generated from:

```text
https://www.nseindia.com/api/holiday-master?type=trading&year=2025
https://www.nseindia.com/api/holiday-master?type=trading&year=2026
```

using the `CM` segment holiday list, weekdays, and explicit special-session
exceptions.

The derivation direction matters: the 245 normal sessions were generated from
NSE's `CM` holiday data before comparing against downloaded CM-UDiFF archive
existence. They were not fitted to the set of files that happened to download.

The source page for the NSE holiday API is:

```text
https://www.nseindia.com/resources/exchange-communication-holidays
```

Raw CM-UDiFF file existence was checked against:

```text
https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_YYYYMMDD_F_0000.csv.zip
```

## Calendar Reconciliation

| Metric | Count |
| --- | ---: |
| Calendar window days | 365 |
| NSE CM holidays inside window | 19 |
| Weekday-minus-holiday sessions | 245 |
| Explicit special sessions | 2 |
| Checked-in expected sessions | 247 |
| Observed CM-UDiFF files | 247 |
| Expected sessions without UDiFF file | 0 |
| UDiFF files outside checked-in sessions | 0 |

The independent normal-session calendar and observed archive list had no
missing expected-session files. The only observed archives outside the
weekday-minus-holiday calendar were the two special sessions listed below.

## Special Sessions

| Date | Reason | Evidence |
| --- | --- | --- |
| 2025-10-21 | Diwali Muhurat trading | NSE CM holiday list marks Diwali Laxmi Pujan as a holiday; CM-UDiFF archive exists |
| 2026-02-01 | Union Budget Sunday trading | Date is a Sunday; CM-UDiFF archive exists |

The 21 October 2025 Muhurat file was inspected directly. Its `SsnId` was `F1`,
the same session identifier observed in normal-session files, and it contained
2,291 `EQ` rows. `SsnId` therefore cannot be used as the V0 special-session
detector; the checked-in calendar is the source of truth.

V0 keeps special sessions in the calendar for raw-file auditing but excludes
them from the default research bar series. Research helpers must return only
`NORMAL` sessions unless a caller explicitly opts into special sessions. This
prevents one-hour Muhurat trading or other unusual exchange sessions from being
counted as ordinary momentum lookback days or execution/signal sessions by
omission.

## Listing-Day Probe

The one-year row scan found no non-positive `PrvsClsgPric` values across
585,893 `EQ` rows. To turn the listing-day inference into a direct check, the
first CM-UDiFF row for a known listing inside the window was inspected.

| Listing | Date | Symbol | ISIN | Open | High | Low | Close | Previous close |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Vikram Solar Limited | 2025-08-26 | VIKRAMSOLR | INE078V01014 | 338.00 | 381.65 | 333.65 | 356.40 | 332.00 |

This confirms that at least this NSE listing-day row populated
`PrvsClsgPric` with a positive value rather than zero or blank. It does not
prove every listing day across the full research window behaves the same way.

## VWAP Boundary Probe

For every `EQ` row in the same one-year file set, the scan computed:

```text
implied_vwap = TtlTrfVal / TtlTradgVol
```

and measured whether it landed outside the official low/high band.

| Metric | Count |
| --- | ---: |
| EQ rows scanned | 585,893 |
| Rows with implied VWAP below low | 0 |
| Rows with implied VWAP above high | 0 |
| Maximum observed outside-band breach | 0 |

This supports keeping D-026's half-paisa tolerance as a conservative buffer for
future files. In the observed year, no tolerance was needed.

## Runtime Policy

The checked-in CSV is the runtime source of truth for this one-year window.
The NSE holiday API and circular/special-session notes are provenance inputs,
not runtime dependencies.

Pipeline validation must fail or quarantine when:

- an expected session has no raw CM-UDiFF file;
- a raw CM-UDiFF file exists for a date absent from the checked-in calendar.

The calendar must be extended by committing the new year holiday source,
generated sessions, and any special-session exceptions before that year enters
a research run.

## Full-Window Dependency

This artifact validates only one year. The full V0 research window needs a
roughly decade-long checked-in session calendar before universe selection can
run. NSE's current holiday API was validated for 2025 and 2026 in this pass;
older-year availability remains an explicit unresolved dependency. If official
NSE historical holiday data cannot be obtained for earlier years, deriving a
calendar from archive existence may become necessary, but that would weaken the
missing-file audit and must be documented before the universe freeze.
