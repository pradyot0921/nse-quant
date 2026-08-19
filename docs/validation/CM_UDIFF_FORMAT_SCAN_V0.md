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

## Loader Implications

- `TradDt` and `BizDt` are present and equal in all sampled files.
- `TckrSymb`, `ISIN`, and `SctySrs` are the symbol, identifier, and series fields.
- OHLC fields are `OpnPric`, `HghPric`, `LwPric`, and `ClsPric`.
- Raw volume is `TtlTradgVol`.
- Raw traded value is `TtlTrfVal` and must be preserved for universe liquidity ranking.
- Number of transactions is `TtlNbOfTxsExctd`.
- The loader must explicitly select `SctySrs == EQ`; non-`EQ` rows are common and must not enter V0 silently.
- BEML's official UDiFF high/low differ from the earlier hand-entered test values. The test is corrected to match these rows before loader implementation starts.
