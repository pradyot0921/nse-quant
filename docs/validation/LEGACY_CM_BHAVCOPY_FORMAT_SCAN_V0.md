# Legacy CM Bhavcopy Format Scan V0

**Date:** 23 August 2026
**Status:** Accepted as legacy-loader input evidence

## Purpose

D-030 fixes the V0 data-audit window as 1 January 2016 through 19 August 2026. D-031 initially selected `Full Bhavcopy and Security Deliverable data` as the pre-UDiFF bridge. This scan tests that assumption against real files before any legacy parser is written.

## Source Candidate Result

The provisional `sec_bhavdata_full_DDMMYYYY.csv` source is rejected for the full V0 window because it did not exist at the tested 2016 and 2019 dates.

| Date | `sec_bhavdata_full` result |
| --- | --- |
| 2016-01-04 | 404 Not Found |
| 2019-06-03 | 404 Not Found |
| 2020-03-23 | available; 1957 rows, 1543 EQ rows |
| 2022-08-01 | available; 2262 rows, 1808 EQ rows |
| 2024-07-05 | available; 2615 rows, 1906 EQ rows |

The legacy source selected for V0 is therefore the older NSE CM bhavcopy ZIP:

```text
https://nsearchives.nseindia.com/content/historical/EQUITIES/YYYY/MMM/cmDDMMMYYYYbhav.csv.zip
```

## Files Inspected

| Date | File | Bytes | Rows | EQ rows | Max VWAP breach |
| --- | --- | ---: | ---: | ---: | ---: |
| 2016-01-04 | `cm04JAN2016bhav.csv.zip` | 59858 | 1623 | 1472 | 0 |
| 2019-06-03 | `cm03JUN2019bhav.csv.zip` | 69294 | 1947 | 1493 | 0 |
| 2020-03-23 | `cm23MAR2020bhav.csv.zip` | 66967 | 1965 | 1548 | 0 |
| 2022-08-01 | `cm01AUG2022bhav.csv.zip` | 85520 | 2279 | 1811 | 0 |
| 2024-07-05 | `cm05JUL2024bhav.csv.zip` | 109203 | 2775 | 1906 | 0 |

Each ZIP contained exactly one CSV member matching the archive date.

## Header

All five files had the same header, including a trailing blank column:

```text
SYMBOL
SERIES
OPEN
HIGH
LOW
CLOSE
LAST
PREVCLOSE
TOTTRDQTY
TOTTRDVAL
TIMESTAMP
TOTALTRADES
ISIN
<blank>
```

The trailing blank column was empty on every scanned EQ row. The parser should tolerate the column only when it is present and empty; any non-empty trailing value is a row/file quality failure.

## Row-Quality Summary

| Date | Duplicate EQ symbols | Bad OHLC/prev close | Non-positive volume/value/trades | Blank ISIN | Timestamp values |
| --- | ---: | ---: | ---: | ---: | --- |
| 2016-01-04 | 0 | 0 | 0 | 0 | `04-JAN-2016=1623` |
| 2019-06-03 | 0 | 0 | 0 | 0 | `03-JUN-2019=1947` |
| 2020-03-23 | 0 | 0 | 0 | 0 | `23-MAR-2020=1965` |
| 2022-08-01 | 0 | 0 | 0 | 0 | `01-AUG-2022=2279` |
| 2024-07-05 | 0 | 0 | 0 | 0 | `05-JUL-2024=2775` |

For all scanned EQ rows, `TOTTRDVAL / TOTTRDQTY` lay inside the daily low/high range with zero observed breach. This supports using `TOTTRDVAL` directly as raw traded value in rupees.

## Series Counts

### 2016-01-04

```text
EQ=1472, BE=52, BZ=10, N2=9, N1=7, N6=7, N5=6, N9=6, N3=5, N4=5, N8=4, N7=3, NB=3, NJ=3, SM=3, NA=2, ND=2, NE=2, BL=1, D1=1, DR=1, NC=1, NF=1, NI=1, NK=1, NL=1, NM=1, NP=1, NS=1, NX=1, NY=1, P1=1, P2=1, W2=1, Y2=1, Y8=1, YA=1, YB=1, YD=1, YG=1
```

### 2019-06-03

```text
EQ=1493, BE=143, SM=89, BZ=37, GB=20, N2=13, N6=10, N8=9, N4=8, MF=7, N1=7, NE=7, N3=6, N5=6, N7=6, NA=6, ND=6, N9=4, NB=3, NC=3, NF=3, NM=3, NN=3, NO=3, NP=3, NS=3, E1=2, IV=2, NH=2, NJ=2, NK=2, NQ=2, NR=2, NX=2, P2=2, Y1=2, YI=2, YJ=2, BL=1, DR=1, E3=1, NG=1, NL=1, NU=1, NY=1, NZ=1, P1=1, RR=1, Y3=1, Y5=1, Y6=1, Y8=1, Y9=1, YG=1, YH=1, YK=1, YL=1, YO=1, YR=1, YV=1
```

### 2020-03-23

```text
EQ=1548, BE=65, SM=63, BZ=44, GB=23, N6=16, N2=15, MF=13, N4=12, N5=11, N1=7, N9=7, GS=6, N3=6, N8=6, NE=6, NA=5, NB=5, NF=5, NJ=5, NN=5, N7=4, NI=4, NL=4, NC=3, ND=3, NG=3, NH=3, NK=3, NO=3, NS=3, IV=2, NP=2, NQ=2, NU=2, NX=2, NY=2, Y3=2, Y9=2, BL=1, DR=1, E1=1, E3=1, NM=1, NR=1, P2=1, RR=1, Y5=1, YB=1, YG=1, YH=1, YI=1, YJ=1, YK=1, YL=1, YM=1, YN=1, YO=1, YP=1, YQ=1, YR=1, YS=1, YT=1, YU=1, YV=1, YW=1, YX=1, YY=1, YZ=1, Z1=1, Z2=1, Z3=1, Z4=1, Z5=1, Z6=1, Z7=1, Z8=1, Z9=1, ZA=1, ZB=1, ZC=1, ZD=1
```

### 2022-08-01

```text
EQ=1811, BE=130, SM=74, GB=52, BZ=32, N6=12, GS=11, N2=11, N4=11, N7=8, N3=7, N8=7, N1=6, N5=6, NA=6, NE=6, ND=5, N9=4, NC=4, NJ=4, E1=3, IV=3, MF=3, NG=3, NH=3, NI=3, NK=3, NL=3, NO=3, RR=3, ST=3, NF=2, NN=2, NQ=2, NY=2, TB=2, Y5=2, NB=1, NP=1, NR=1, NS=1, NT=1, NU=1, NX=1, SZ=1, W3=1, X1=1, Y3=1, Y8=1, YA=1, YH=1, YI=1, YK=1, YL=1, YN=1, YO=1, YP=1, YV=1, YW=1, Z3=1, Z5=1, Z7=1, ZD=1, ZI=1
```

### 2024-07-05

```text
EQ=1906, SM=278, BE=262, GB=58, GS=46, ST=31, TB=20, BZ=16, N6=12, N5=10, N2=9, NA=9, N4=7, N8=7, N0=6, N3=6, NC=6, E1=5, IV=5, N7=5, N9=5, ND=4, NE=4, NJ=4, RR=4, NF=3, NG=2, NH=2, NK=2, NL=2, NN=2, NO=2, NS=2, Z5=2, AG=1, AP=1, AY=1, BC=1, BF=1, N1=1, NB=1, NI=1, NM=1, NR=1, NT=1, NU=1, NV=1, NW=1, NX=1, NZ=1, P1=1, SG=1, SZ=1, W1=1, Y0=1, Y1=1, Y3=1, YL=1, YP=1, YV=1, YW=1, YZ=1, Z4=1, ZD=1, ZF=1
```

## Canonical Mapping

| Canonical field | Legacy CM bhavcopy field |
| --- | --- |
| `trade_date` | `TIMESTAMP` |
| `source_format` | `literal `NSE_CM_BHAVCOPY_CSV_ZIP`` |
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
| `source_file` | `archive filename and CSV member` |

Delivery quantity and delivery percentage are not present in this source and must remain absent/null in the canonical manifest rather than fabricated.

## Parser Requirements

- Accept only a ZIP containing exactly one CSV.
- Require the exact observed header, including an empty trailing column, unless a later scan records a versioned schema change.
- Filter V0 research rows to `SERIES == EQ`; report all other series counts explicitly.
- Convert OHLC, previous close, last, and raw traded value to `Decimal` at ingestion.
- Treat non-positive OHLC, previous close, traded volume, traded value, or trade count as row-level rejections.
- Require non-blank ISIN for EQ rows in the scanned legacy schema.
- Apply the same traded-value VWAP range invariant used for UDiFF: `TOTTRDVAL / TOTTRDQTY` must lie inside low/high after the documented tolerance.

## Consequence

D-031 is superseded by D-032 for the pre-UDiFF source choice. The legacy segment should use CM bhavcopy ZIPs, not `Full Bhavcopy and Security Deliverable data`.
