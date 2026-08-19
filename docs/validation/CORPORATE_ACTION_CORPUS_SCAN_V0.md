# NSE Corporate-Action Parser Corpus Scan V0

Source: NSE corporate actions endpoint, `index=equities`
Window: `19-08-2025` to `19-08-2026`
Rows in endpoint: `2028`
EQ rows scanned: `1866`

This scan validates the conservative corporate-action parser against one year of real NSE EQ-series purpose strings before applying adjustments to research data.

## Category Frequency

| Category | Count |
|---|---:|
| SPLIT | 52 |
| BONUS | 49 |
| IGNORED | 1713 |
| UNSUPPORTED | 52 |

## Unsupported Purposes

These records intentionally remain quarantined in V0. A universe symbol with one of these unsupported actions in the research window must fail dataset validation unless a later decision adds deterministic support or explicitly reclassifies the action.

| Count | Purpose |
|---:|---|
| 12 | Demerger |
| 1 | Rights 12:47 @ Premium Rs 5/- |
| 1 | Scheme Of Arrangement - Bonus Ncrps 4:1 |
| 1 | Rights 3:4 @ Premium Rs 78/- |
| 1 | Rights 3:5 @ Premium Rs 38/- |
| 1 | Rights 2:9 @ Premium Rs 7/- |
| 1 | Rights 1:1 @ Premium Rs 4/- |
| 1 | Rights 23:49 @ Premium Rs 181/- |
| 1 | Rights 8:13 @ Premium Rs 4/- |
| 1 | Rights 3:19 @ Premium Rs 18/- |
| 1 | Rights 1:4 @ Premium Rs 8/- |
| 1 | Rights 3:25 @ Premium Rs 1799/- |
| 1 | Rights 1:4 @ Premium Rs 5.35/- |
| 1 | Rights 7:40 @ Premium Rs 26/- |
| 1 | Rights 277:630 @ Premium Rs 11.50/- |
| 1 | Rights 5:31 @ Premium Rs 75.70/- |
| 1 | Rights 45:301 @ Premium Rs 290/- |
| 1 | Rights 13:12 @ Premium Rs 20/- |
| 1 | Rights 14:29 @ Premium Rs 18.32/- |
| 1 | Rights 3:10 @ Premium Rs 50/- |
| 1 | Rights 19:41 @ Premium Rs 89/- |
| 1 | Rights 300:167 @ Premium Rs 5/- |
| 1 | Rights 11:5 @ Premium Rs 54/- |
| 1 | Rights 8:1 @ Premium Rs 0/- |
| 1 | Rights 29:60 @ Premium Rs 6.68/- |
| 1 | Rights 4:5 @ Premium Rs 1.56/- |
| 1 | Rights 1:17 @ Premium Rs 502/- |
| 1 | Rights 5:14 @ Premium Rs 143/- |
| 1 | Rights 1:2 @ Premium Rs 290/- |
| 1 | Rights 1:1 @ Premium Rs 0/- |
| 1 | Rights 11:64 @ Premium Rs 155/- |
| 1 | Rights 8:103 @ Premium Rs 148/- |
| 1 | Rights 161:250 @ Premium Re 0.45 /- |
| 1 | Rights 8:33 @ Premium Rs 135/- |
| 1 | Rights 36:311 @ Premium Rs 3.86 |
| 1 | Rights 1:9 @ Premium 91 |
| 1 | Rights 8:25 @ Premium Rs 9.86/- |
| 1 | Rights 3:2 @ Premium Re. 0.63/- |
| 1 | Rights 19:295 @ Premium Rs 205/- |
| 1 | Rights 3:5 @ Premium Rs 45/- |
| 1 | Rights 2:5 @ Premium Rs 1.17/- |

## Parsed Split And Bonus Purposes

| Category | Count | Purpose | Price Factor | Volume Factor | Example |
|---|---:|---|---:|---:|---|
| BONUS | 1 | Bonus 10:1 | 0.0909090909 | 11.0000000000 | KOTYARK 2026-06-24 |
| BONUS | 21 | Bonus 1:1 | 0.5000000000 | 2.0000000000 | AARON 2025-08-25 |
| BONUS | 2 | Bonus 1:10 | 0.9090909091 | 1.1000000000 | ORIENTTECH 2026-01-05 |
| BONUS | 4 | Bonus 1:2 | 0.6666666667 | 1.5000000000 | BESTAGRO 2026-01-16 |
| BONUS | 3 | Bonus 1:3 | 0.7500000000 | 1.3333333333 | CUB 2026-06-12 |
| BONUS | 1 | Bonus 1:5 | 0.8333333333 | 1.2000000000 | KARURVYSYA 2025-08-26 |
| BONUS | 8 | Bonus 2:1 | 0.3333333333 | 3.0000000000 | PATANJALI 2025-09-11 |
| BONUS | 1 | Bonus 2:5 | 0.7142857143 | 1.4000000000 | HARDWYN 2026-07-28 |
| BONUS | 2 | Bonus 3:1 | 0.2500000000 | 4.0000000000 | INFOBEAN 2026-02-27 |
| BONUS | 3 | Bonus 4:1 | 0.2000000000 | 5.0000000000 | FCL 2025-10-31 |
| BONUS | 1 | Bonus 5:1 | 0.1666666667 | 6.0000000000 | ZFCVINDIA 2026-06-24 |
| BONUS | 1 | Bonus 5:7 | 0.5833333333 | 1.7142857143 | RMDRIP 2026-04-10 |
| BONUS | 1 | Bonus 7:5 | 0.4166666667 | 2.4000000000 | LGHL 2025-10-10 |
| SPLIT | 19 | Face Value Split (Sub-Division) - From Rs 10/- Per Share To Re 1/- Per Share | 0.1000000000 | 10.0000000000 | PAVNAIND 2025-09-01 |
| SPLIT | 16 | Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 2/- Per Share | 0.2000000000 | 5.0000000000 | ZYDUSWELL 2025-09-18 |
| SPLIT | 6 | Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 5/- Per Share | 0.5000000000 | 2.0000000000 | BEML 2025-11-03 |
| SPLIT | 5 | Face Value Split (Sub-Division) - From Rs 2/- Per Share To Re 1/- Per Share | 0.5000000000 | 2.0000000000 | GOKULAGRO 2025-10-14 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 4/- Per Share To Rs 2/- Per Share | 0.5000000000 | 2.0000000000 | NAZARA 2025-09-26 |
| SPLIT | 3 | Face Value Split (Sub-Division) - From Rs 5/- Per Share To Re 1/- Per Share | 0.2000000000 | 5.0000000000 | STEELCAS 2025-08-29 |
| SPLIT | 2 | Face Value Split (Sub-Division) - From Rs 5/- Per Share To Rs 2/- Per Share | 0.4000000000 | 2.5000000000 | DEVIT 2025-08-21 |

## Resolved Follow-Up Checks

- Bonus ratio convention was verified against official NSE CM-UDiFF bhavcopy data. PATANJALI `Bonus 2:1` on 11 September 2025 opened 0.34% from the expected one-third adjusted prior close and 33.11% from the inverted half-factor convention. BEML's 10-to-5 split on 3 November 2025 opened 0.54% from the expected half-factor adjusted prior close.
- `Buy Back` is reclassified as `IGNORED` for price and volume adjustment. Structurally, tender-offer and open-market buybacks do not multiply or dilute the holdings of non-participating shareholders. INFY's 14 November 2025 buyback window corroborated this with no mechanical price step.
- Rights issues remain unsupported in V0. Symbols with a rights issue in the research window are excluded from the frozen V0 universe unless a later decision adds deterministic rights adjustment support.
- UDiFF row-level ISIN changes are an independent validation signal. An ISIN change without a same-date split, bonus, or quarantined corporate-action record must halt or quarantine the symbol/date as a possible missing corporate action.
