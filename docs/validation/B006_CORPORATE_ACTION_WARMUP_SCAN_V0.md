# B006 Corporate-Action Warm-Up Scan V0

Source: NSE corporate actions endpoint, `index=equities`
Window: `2015-01-02` to `2015-12-31`
Chunking: `year`
Endpoint rows: `1911`
EQ rows scanned: `1883`

This scan validates the conservative corporate-action parser against the
pre-2016 input-only warm-up window required by B006. It is not a universe
selection artifact and does not inspect validation-period strategy output.

## Category Frequency

| Category | Count |
| --- | ---: |
| SPLIT | 30 |
| BONUS | 26 |
| IGNORED | 1791 |
| UNSUPPORTED | 36 |

## Chunk Row Counts

| From | To | Endpoint Rows |
| --- | --- | ---: |
| 2015-01-02 | 2015-12-31 | 1911 |

## Endpoint Series Counts

| Series | Rows |
| --- | ---: |
| DR | 3 |
| EQ | 1883 |
| H1 | 2 |
| H2 | 1 |
| H3 | 3 |
| H4 | 2 |
| H5 | 4 |
| H6 | 1 |
| H7 | 2 |
| H8 | 1 |
| H9 | 2 |
| HA | 1 |
| HB | 2 |
| HC | 1 |
| HD | 2 |
| HE | 1 |

## Unsupported Purposes

These records intentionally remain quarantined in V0. A selected B006 warm-up
symbol with one of these unsupported actions inside the required input window
blocks the warm-up dataset unless a later decision adds deterministic support.

| Count | Symbols | Purpose | First Example |
| ---: | ---: | --- | --- |
| 4 | 4 | Scheme Of Arrangement | BALKRISIND 2015-03-24 |
| 3 | 3 | Bonus 1 : 1 | PERSISTENT 2015-03-10 |
| 3 | 3 | Demerger | ASAHISONG 2015-02-02 |
| 3 | 2 | E-Voting | ESL 2015-01-08 |
| 1 | 1 | Annual General Meetig | UNITY 2015-09-10 |
| 1 | 1 | Annual General Meeting/Scheme Of Arrangement | GOKUL 2015-09-16 |
| 1 | 1 | Annual General Meetng | PFOCUS 2015-12-10 |
| 1 | 1 | Bonus 1 : 1250 | GODREJIND 2015-01-05 |
| 1 | 1 | Bonus 1:1 / Face Value Split - From Rs 10/- Per Share To Rs 5/- Per Share | TECHM 2015-03-19 |
| 1 | 1 | Bonus 1:1 / Face Value Split From Rs 10/- Per Share To Rs 2/- Per Share | MINDACORP 2015-01-05 |
| 1 | 1 | Composite Scheme Of Arrangement | JSL 2015-11-19 |
| 1 | 1 | Face Value Split Rs 10 To Rs 1 | GRANULES 2015-03-23 |
| 1 | 1 | Face Valus Split (Sub-Division) - From Rs 10/- Per To Rs 2/- Per Share | CORPBANK 2015-01-22 |
| 1 | 1 | For Distribution Of Chennai Super Kings Cricket Limited Shares To The Shareholders Of India Cements | INDIACEM 2015-10-08 |
| 1 | 1 | Interim Divdend - Rs 5/- Per Share | POLARIS 2015-03-30 |
| 1 | 1 | Rights 14:19 @ Premium Rs 5/- Per Share | VASCONEQ 2015-06-23 |
| 1 | 1 | Rights 1:2 @ Premium Rs.41/- Per Share | UNIVCABLES 2015-09-16 |
| 1 | 1 | Rights 1:3 @ Premium Rs.80/- Per Share | IL&FSTRANS 2015-10-07 |
| 1 | 1 | Rights 1:5 @ Premium Rs 390/- Per Share | SBT 2015-03-03 |
| 1 | 1 | Rights 3:10 @ Premium Rs 17/- Per Share | ZEEMEDIA 2015-03-16 |
| 1 | 1 | Rights 3:10 @ Premium Rs 440/- Per Share | CANFINHOME 2015-01-23 |
| 1 | 1 | Rights 3:14 @ Premium Rs 14/- Per Share | GMRAIRPORT 2015-03-11 |
| 1 | 1 | Rights 6:109 @ Premium Rs. 448/- Per Share | TMPV 2015-04-06 |
| 1 | 1 | Rights 6:109 @ Premium Rs.269/- Per Share | TATAMTRDVR 2015-04-06 |
| 1 | 1 | Rights : 24:10 At Par | ASHIMASYN 2015-10-30 |
| 1 | 1 | Scheme Of Arrangement - Bonus Debentures 1:1 | NTPC 2015-03-20 |
| 1 | 1 | Scheme Of Arrangement-To Ascertain Eligible Members To Provide Option To Opt For Ncd In Place Of Equity Shares | INTELLECT 2015-01-16 |

## Parsed Split And Bonus Purposes

| Category | Count | Purpose | Price Factor | Volume Factor | First Example |
| --- | ---: | --- | ---: | ---: | --- |
| BONUS | 1 | Annual General Meeting / Dividend - Rs 3/- Per Share / Bonus - 1:2 | 0.6666666667 | 1.5000000000 | MOTHERSON 2015-07-23 |
| BONUS | 1 | Annual General Meeting/ Dividend - Rs 29.50/- Per Share And Bonus 1:1 | 0.5000000000 | 2.0000000000 | INFY 2015-06-15 |
| BONUS | 1 | Bonus 10:1 | 0.0909090909 | 11.0000000000 | VIVIDHA 2015-05-28 |
| BONUS | 2 | Bonus 1: 1 | 0.5000000000 | 2.0000000000 | KOTAKBANK 2015-07-08 |
| BONUS | 16 | Bonus 1:1 | 0.5000000000 | 2.0000000000 | FCL 2015-02-12 |
| BONUS | 2 | Bonus 1:2 | 0.6666666667 | 1.5000000000 | INSECTICID 2015-04-16 |
| BONUS | 1 | Bonus 1:3 | 0.7500000000 | 1.3333333333 | ECLERX 2015-12-17 |
| BONUS | 1 | Bonus 1:6 | 0.8571428571 | 1.1666666667 | MOHOTAIND 2015-03-16 |
| BONUS | 1 | Bonus 2:1 | 0.3333333333 | 3.0000000000 | BEL 2015-09-14 |
| SPLIT | 4 | Face Value Split (Sub-Division) - From Rs 10/- Per Share To Re 1/- Per Share | 0.1000000000 | 10.0000000000 | KANSAINER 2015-03-26 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 1/- Per Share | 0.1000000000 | 10.0000000000 | SIGNET 2015-08-17 |
| SPLIT | 8 | Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 2/- Per Share | 0.2000000000 | 5.0000000000 | HATHWAY 2015-01-06 |
| SPLIT | 5 | Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 5/- Per Share | 0.5000000000 | 2.0000000000 | POLYMED 2015-02-02 |
| SPLIT | 2 | Face Value Split (Sub-Division) - From Rs 2/- Per Share To Re 1/- Per Share | 0.5000000000 | 2.0000000000 | BERGEPAINT 2015-01-08 |
| SPLIT | 2 | Face Value Split (Sub-Division) - From Rs 5/- Per Share To Re 1/- Per Share | 0.2000000000 | 5.0000000000 | MENONBE 2015-04-09 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 5/- Per Share To Rs 2/- Per Share | 0.4000000000 | 2.5000000000 | AJANTPHARM 2015-03-20 |
| SPLIT | 1 | Face Value Split (Sub-Division): From Rs 10/- Per Share To Re 1/- Per Share | 0.1000000000 | 10.0000000000 | TATACOFFEE 2015-01-23 |
| SPLIT | 1 | Face Value Split (Sub-Division): From Rs 10/- Per Share To Rs 2/- Per Share | 0.2000000000 | 5.0000000000 | HIKAL 2015-02-27 |
| SPLIT | 1 | Face Value Split From Rs 10 To Re 1 (Record Date Revised) | 0.1000000000 | 10.0000000000 | SARLAPOLY 2015-10-29 |
| SPLIT | 1 | Face Value Split From Rs 10 To Rs 1 | 0.1000000000 | 10.0000000000 | AEGISLOG 2015-09-16 |
| SPLIT | 1 | Face Value Split From Rs 10 To Rs 5 | 0.5000000000 | 2.0000000000 | LAMBODHARA 2015-10-15 |
| SPLIT | 1 | Face Valus Split (Sub-Division) - From Rs 10/- Per Share To Rs 2/- Per Share | 0.2000000000 | 5.0000000000 | FCL 2015-06-11 |
| SPLIT | 1 | Interim Dividend - Rs 1.50/- Per Share / Face Value Split - From Rs 10/- Per Share To Rs 5/- Per Share (Purpose Revised) | 0.5000000000 | 2.0000000000 | RSSOFTWARE 2015-01-21 |

## Row-Level Failures

None.

## Interpretation

This report is a warm-up corpus scan, not a universe freeze and not a strategy
result. It identifies the 2015 corporate-action vocabulary that the V0 parser
can and cannot classify deterministically before B006 warm-up data is trusted.
