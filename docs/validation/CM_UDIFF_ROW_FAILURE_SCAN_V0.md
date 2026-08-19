# CM-UDiFF Row Failure Scan V0

**Date:** 20 August 2026
**Status:** Accepted as loader error-model evidence

## Source

Downloaded NSE CM-UDiFF common bhavcopy ZIP files from:

```text
https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_YYYYMMDD_F_0000.csv.zip
```

The scan covered calendar dates from 20 August 2025 through 19 August 2026.
Archive `404` responses were counted as missing/non-session dates for this
scan; the version-controlled trading-session calendar remains the authoritative
source for production missing-file validation.

## Method

Each available file was checked with the PR #9 parser's file-level validations:

- exact 34-column schema
- non-empty file
- single `TradDt`
- single `BizDt`
- `TradDt == BizDt`
- filename date matching `TradDt`

Within files that passed those checks, every `EQ` row was passed through the
strict row validations used by `parse_cm_udiff_file()`. Row failures were
collected instead of being allowed to abort the file, so the scan could measure
the row-level failure distribution.

## Summary

| Metric | Count |
| --- | ---: |
| Calendar dates attempted | 365 |
| UDiFF files downloaded/found | 247 |
| Missing or non-session dates | 118 |
| Download errors | 0 |
| File-level parser errors | 0 |
| Files with rejected `EQ` rows | 0 |
| Total rows scanned | 816,308 |
| Total `EQ` rows scanned | 585,893 |
| Valid `EQ` rows | 585,893 |
| Rejected `EQ` rows | 0 |

## Rejection Distribution

No `EQ` rows failed the strict row checks in this one-year window.

```text
rejection_reasons = []
rejected_symbols = []
```

## Interpretation

The scan supports keeping the strict row invariants: in recent real NSE
CM-UDiFF data they did not produce noisy row rejection.

It does not prove malformed or non-tradeable rows cannot appear across the full
research window. A decade-long V0 build will scan millions of rows, including
listings, suspensions, halts, and data-quality edge cases not necessarily
present in this one-year sample.

The loader therefore keeps file-level failures fatal but returns row-level
failures as explicit rejected rows. Downstream validation can then fail only
when the rejected symbol/date matters to the frozen universe or breaches the
missing-bar tolerance, instead of losing an entire trading session because one
row is malformed.

## Follow-Up

- Re-run this scan over the full research window before freezing the V0
  universe.
- Report rejected row counts and reasons in the universe-freeze artifact.
- Treat any rejected row for a held symbol as a no-fill/stale-price event under
  D-027 unless a later decision defines a more specific policy.
