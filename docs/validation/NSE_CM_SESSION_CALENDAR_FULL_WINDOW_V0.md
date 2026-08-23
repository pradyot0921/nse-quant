# NSE CM Full-Window Session Calendar V0

**Date:** 23 August 2026  
**Status:** Accepted as the V0 full-window calendar artifact

## Scope

The checked-in calendar covers the full Phase 1 V0 data-audit window:

```text
2016-01-01 through 2026-08-19, inclusive
```

Runtime artifact:

```text
data/calendars/nse_cm_sessions_2016-01-01_2026-08-19.csv
```

The CSV uses the compact two-column runtime format: `START` and `END` define
the inclusive window, `H` rows remove weekday holidays, and `S` rows add
special-session exceptions. Only weekday holiday exclusions require `H` rows;
weekend holiday API rows are counted in the evidence below but do not affect
runtime expansion. Full construction evidence is recorded in this validation
note.

## Derivation

Normal sessions were generated from NSE's Capital Market trading-holiday API
for calendar years 2016 through 2026:

```text
https://www.nseindia.com/api/holiday-master?type=trading&year=YYYY
```

The runtime calendar was not derived from downloaded market-data files.
Normal sessions are weekdays inside the V0 window minus NSE `CM` holidays.

Special sessions are explicit exceptions. They were not inferred from weekdays.
Each included special session has a matching NSE daily archive.

## Counts

| Metric | Count |
| --- | ---: |
| Window days | 3,884 |
| NSE CM holidays inside window | 201 |
| Normal sessions | 2,618 |
| Special sessions | 13 |
| Total checked-in sessions | 2,631 |

## Special Sessions

| Date | Type | Archive probe |
| --- | --- | --- |
| 2016-10-30 | Diwali Muhurat trading | 206 |
| 2017-10-19 | Diwali Muhurat trading | 206 |
| 2018-11-07 | Diwali Muhurat trading | 206 |
| 2019-10-27 | Diwali Muhurat trading | 206 |
| 2020-02-01 | Union Budget Saturday trading | 206 |
| 2020-11-14 | Diwali Muhurat trading | 206 |
| 2021-11-04 | Diwali Muhurat trading | 206 |
| 2022-10-24 | Diwali Muhurat trading | 206 |
| 2023-11-12 | Diwali Muhurat trading | 206 |
| 2024-11-01 | Diwali Muhurat trading | 206 |
| 2025-02-01 | Union Budget Saturday trading | 206 |
| 2025-10-21 | Diwali Muhurat trading | 206 |
| 2026-02-01 | Union Budget Sunday trading | 206 |

The archive probe used one-byte range requests against the registered source
family for each date: legacy `CM - Bhavcopy(csv)` through 5 July 2024 and
CM-UDiFF from 8 July 2024 onward.

## Evidence Notes

The NSE holiday API directly marks some Muhurat dates, including
`Diwali-Laxmi Pujan*` rows. Other historical Muhurat dates are weekday special
sessions that are not distinguishable from normal weekdays by the holiday API
alone, so they are explicit exceptions.

Public exchange/broker/news references were used to identify the historical
Muhurat and Budget-session dates, and NSE archive existence was checked for
each included exception.

References used during construction include:

- NSE holiday page: `https://www.nseindia.com/resources/exchange-communication-holidays`
- NSE archive root: `https://nsearchives.nseindia.com/`
- 2016 Muhurat notice mirror: `https://www.cse-india.com/upload/CSE%20Notices%20%26%20Circulars/2016/Notice261016_2.htm`
- 2017 Muhurat notice: `https://upstox.com/market-talk/right-trade-at-the-right-muhurat/`
- 2018 Muhurat notice mirror: `https://www.cse-india.com/upload/cse_notice/Muhurat_Trading_Session_on_account_of_Diwali1.htm`
- 2021 Muhurat report: `https://indianexpress.com/article/business/market/muhurat-trading-diwali-2021-samvat-2078-live-updates-stocks-shares-bse-sensex-nse-nifty-november-4-7607540/lite/`
- 2022 Muhurat report: `https://indianexpress.com/article/business/market/diwali-muhurat-trading-2022-samvat-2079-live-updates-shares-bse-sensex-nse-nifty-october-24-8227782/`
- 2024 Muhurat notice: `https://zerodha.com/marketintel/bulletin/393613/muhurat-trading-session-on-account-of-diwali-november-2024`
- 2020 Budget trading notice: `https://zerodha.com/marketintel/bulletin/242887/stock-market-to-remain-open-on-saturday-february-1st-2020`
- 2025 Budget trading report: `https://www.moneycontrol.com/news/business/stocks/budget-2025-will-nifty-sensex-remain-open-for-trade-on-saturday-february-1-12922254.html`
- 2026 Budget trading notice: `https://zerodha.com/marketintel/bulletin/439957/special-live-trading-session-on-sunday-february-1-2026`

## Runtime Policy

This file supersedes the one-year 2025-2026 calendar for full Phase 1 V0
dataset construction. The one-year file remains as validation history.

Special sessions remain in the calendar for raw-file auditing but are excluded
from default research bars under D-029.

If the batch acquisition pass later finds:

- a missing archive for a checked-in session, or
- an archive on a date absent from this calendar,

the result must be recorded and resolved before dataset construction proceeds.
Such archive outcomes do not rewrite the calendar silently.
