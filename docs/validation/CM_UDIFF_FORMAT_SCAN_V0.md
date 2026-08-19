# CM-UDiFF Format Scan V0

**Date:** 20 August 2026
**Status:** Accepted as loader input evidence

## Source

NSE lists `CM-UDiFF Common Bhavcopy Final (zip)` under All Reports for
equities. NSE's forms and formats page identifies UDiFF as the standardised
file format for exchange trade and bhavcopy files.

Date-specific files were downloaded from:

```text
https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_YYYYMMDD_F_0000.csv.zip
```

## Files Inspected

| Date | File | Rows | Columns | Series counts, top observed |
| --- | --- | ---: | ---: | --- |
| 2025-10-31 | BhavCopy_NSE_CM_0_0_0_20251031_F_0000.csv.zip | 3189 | 34 | EQ=2283, SM=377, BE=147, ST=66 |
| 2025-11-03 | BhavCopy_NSE_CM_0_0_0_20251103_F_0000.csv.zip | 3216 | 34 | EQ=2286, SM=368, BE=159, ST=64 |
| 2026-07-13 | BhavCopy_NSE_CM_0_0_0_20260713_F_0000.csv.zip | 3451 | 34 | EQ=2378, BE=309, SM=289, ST=149 |

Two additional files were inspected only to verify already-committed
PATANJALI real-bar test data:

| Date | Symbol | Open | High | Low | Close | Volume | ISIN |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 2025-09-10 | PATANJALI | 1810.00 | 1810.00 | 1788.00 | 1802.00 | 286019 | INE619A01035 |
| 2025-09-11 | PATANJALI | 602.70 | 603.50 | 589.50 | 598.90 | 2427699 | INE619A01035 |

## Observed Header

All three primary files had the same 34 columns:

```text
TradDt
BizDt
Sgmt
Src
FinInstrmTp
FinInstrmId
ISIN
TckrSymb
SctySrs
XpryDt
FininstrmActlXpryDt
StrkPric
OptnTp
FinInstrmNm
OpnPric
HghPric
LwPric
ClsPric
LastPric
PrvsClsgPric
UndrlygPric
SttlmPric
OpnIntrst
ChngInOpnIntrst
TtlTradgVol
TtlTrfVal
TtlNbOfTxsExctd
SsnId
NewBrdLotQty
Rmks
Rsvd1
Rsvd2
Rsvd3
Rsvd4
```

## Sample EQ Rows

| Date | Symbol | Series | ISIN | Open | High | Low | Close | Volume | Traded value |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2025-10-31 | 20MICRONS | EQ | INE144J01027 | 206.72 | 207.90 | 204.76 | 206.83 | 60289 | 12469338.81 |
| 2025-11-03 | 20MICRONS | EQ | INE144J01027 | 206.83 | 221.20 | 206.83 | 217.71 | 218244 | 47023978.03 |
| 2026-07-13 | 20MICRONS | EQ | INE144J01027 | 197.54 | 207.10 | 193.67 | 202.45 | 210941 | 42731255.85 |

## BEML Split Rows

| Date | Symbol | Series | ISIN | Open | High | Low | Close | Volume | Traded value |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2025-10-31 | BEML | EQ | INE258A01016 | 4453.70 | 4505.00 | 4382.90 | 4399.80 | 349959 | 1554003341.40 |
| 2025-11-03 | BEML | EQ | INE258A01024 | 2188.00 | 2209.00 | 2164.00 | 2187.00 | 333246 | 727833459.60 |

## Full Series Counts

The top-four summary above is not sufficient for validation, because roughly
320 rows per primary file are in other series. The loader must use `EQ` as an
allowlist, reject/report every non-`EQ` row, and flag any previously unseen
series code in validation output.

```text
2025-10-31:
AI=1, AL=1, BE=147, BZ=30, E1=9, EQ=2283, GB=51, GS=52,
IV=11, N0=12, N1=7, N2=9, N3=2, N4=4, N5=4, N6=9,
N7=7, N8=5, N9=5, NA=6, NB=2, NC=7, ND=6, NE=6,
NF=2, NG=3, NH=3, NI=2, NJ=4, NK=1, NL=2, NM=1,
NN=3, NO=1, NP=1, NQ=1, NR=2, NS=2, NT=1, NU=1,
NV=1, NZ=2, P1=1, RR=5, SG=3, SM=377, ST=66, SZ=1,
T0=4, TB=9, X1=1, Y8=1, YI=1, YL=1, YM=1, YS=1,
YW=1, YZ=1, Z5=1, ZC=1, ZJ=1, ZN=1, ZT=1, ZX=1

2025-11-03:
AK=1, BE=159, BZ=42, E1=9, EQ=2286, GB=49, GS=55,
IV=10, N0=13, N1=10, N2=7, N3=4, N4=7, N5=5, N6=11,
N7=5, N8=5, N9=6, NA=9, NB=4, NC=6, ND=7, NE=6,
NF=4, NG=2, NH=3, NI=1, NJ=3, NK=1, NL=2, NN=2,
NO=1, NR=2, NS=1, NT=2, NU=1, NV=1, P1=1, RR=5,
SG=8, SM=368, ST=64, SZ=2, T0=1, TB=11, X1=1, Y1=2,
Y5=1, YA=1, YP=1, YR=1, YS=1, YW=1, Z5=1, ZF=1,
ZJ=1, ZT=1, ZX=1

2026-07-13:
BE=309, BL=1, BZ=38, E1=2, EQ=2378, GB=39, GS=56,
IV=10, N0=23, N1=12, N2=14, N3=5, N4=6, N5=8, N6=7,
N7=3, N8=4, N9=6, NA=7, NB=2, NC=3, ND=4, NE=6,
NF=3, NG=1, NH=2, NI=1, NJ=4, NK=2, NL=1, NM=3,
NN=2, NO=2, NR=1, NS=2, NT=1, NU=1, NZ=1, P1=1,
RR=6, SG=7, SM=289, ST=149, SZ=1, TB=13, Y0=1, Y1=1,
Y3=1, Y4=1, Y6=1, Y9=1, YC=1, YI=1, YL=1, YW=1,
YZ=1, Z8=1, Z9=1, ZC=1, ZT=1
```

## Data-Quality Probes

| Check | 2025-10-31 | 2025-11-03 | 2026-07-13 |
| --- | ---: | ---: | ---: |
| Distinct `SsnId` values | F1 | F1 | F1 |
| Zero-volume rows | 0 | 0 | 0 |
| Zero-volume `EQ` rows | 0 | 0 | 0 |
| Duplicate `TckrSymb` inside `EQ` rows | 0 | 0 | 0 |

The two PATANJALI verification files dated 2025-09-10 and 2025-09-11 also had
only `SsnId=F1`, no zero-volume rows, no zero-volume `EQ` rows, and no duplicate
`EQ` symbols.

`SsnId` did not vary in these normal-session files. It is therefore not yet
evidence that special sessions such as Muhurat trading can be detected from
`SsnId`; D-023's explicit special-session exception list remains required.

## Traded-Value Check

`TtlTrfVal` is the exchange-provided raw traded-value field. It is not
equivalent to close multiplied by volume.

For BEML on 2025-10-31:

```text
TtlTrfVal                = 1554003341.40
ClsPric * TtlTradgVol    = 4399.80 * 349959 = 1539749608.20
Difference               = 0.9172% of TtlTrfVal
Implied VWAP             = 4440.53
Official low/high        = 4382.90 / 4505.00
```

The implied VWAP sits inside the day's official price range, so `TtlTrfVal` is
the correct liquidity input and close-times-volume is only an approximation.

## Loader Implications

- `TradDt` and `BizDt` are present and equal in all sampled files.
- `TckrSymb`, `ISIN`, and `SctySrs` are the symbol, identifier, and series fields.
- OHLC fields are `OpnPric`, `HghPric`, `LwPric`, and `ClsPric`.
- Raw volume is `TtlTradgVol`.
- Raw traded value is `TtlTrfVal`; it is authoritative for UDiFF liquidity ranking and must be preserved.
- `TtlTrfVal / TtlTradgVol` must lie inside the daily low/high range for every valid `EQ` row.
- Number of transactions is `TtlNbOfTxsExctd`.
- The loader must explicitly select `SctySrs == EQ`; non-`EQ` rows are common and must not enter V0 silently.
- A zero-volume or zero-traded-value `EQ` row is not a valid tradeable OHLCV bar in V0 and must be reported or quarantined rather than carried forward.
- Duplicate `EQ` symbols were not observed in the sampled files, but loader validation should still reject duplicates within one file.
- BEML's official UDiFF high/low differ from the earlier hand-entered test values. The test is corrected to match these rows before loader implementation starts.
