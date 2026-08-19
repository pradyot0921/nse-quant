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

## Special Sessions

| Date | Reason | Evidence |
| --- | --- | --- |
| 2025-10-21 | Diwali Muhurat trading | NSE CM holiday list marks Diwali Laxmi Pujan as a holiday; CM-UDiFF archive exists |
| 2026-02-01 | Union Budget Sunday trading | Date is a Sunday; CM-UDiFF archive exists |

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
