# NSE Corporate-Action Full-Window Scan V0

Source: NSE corporate actions endpoint, `index=equities`
Window: `2016-01-01` to `2026-08-19`
Chunking: `year`
Endpoint rows: `23734`
EQ rows scanned: `22391`

This scan validates the conservative corporate-action parser against the
full pre-registered research and validation window before universe
selection.

## Category Frequency

| Category | Count |
| --- | ---: |
| SPLIT | 376 |
| BONUS | 405 |
| IGNORED | 21163 |
| UNSUPPORTED | 447 |

## Chunk Row Counts

| From | To | Endpoint Rows |
| --- | --- | ---: |
| 2016-01-01 | 2016-12-31 | 2106 |
| 2017-01-01 | 2017-12-31 | 2025 |
| 2018-01-01 | 2018-12-31 | 2012 |
| 2019-01-01 | 2019-12-31 | 2148 |
| 2020-01-01 | 2020-12-31 | 2208 |
| 2021-01-01 | 2021-12-31 | 2325 |
| 2022-01-01 | 2022-12-31 | 2483 |
| 2023-01-01 | 2023-12-31 | 2587 |
| 2024-01-01 | 2024-12-31 | 2693 |
| 2025-01-01 | 2025-12-31 | 1927 |
| 2026-01-01 | 2026-08-19 | 1220 |

## Endpoint Series Counts

| Series | Rows |
| --- | ---: |
| DR | 5 |
| EQ | 22391 |
| GS | 933 |
| H5 | 2 |
| H6 | 1 |
| H7 | 1 |
| H8 | 1 |
| H9 | 5 |
| HA | 1 |
| HB | 6 |
| HC | 1 |
| HD | 6 |
| HE | 1 |
| IV | 296 |
| RR | 84 |

## Unsupported Purposes

These records intentionally remain quarantined in V0. A universe candidate
with one of these unsupported actions inside the frozen window must be
excluded unless a later decision adds deterministic support before
universe selection.

| Count | Symbols | Purpose | First Example |
| ---: | ---: | --- | --- |
| 87 | 82 | Demerger | ARVIND 2018-11-28 |
| 28 | 26 | Scheme Of Arrangement | ABIRLANUVO 2016-01-20 |
| 4 | 4 | Rights 1:1 @ Premium Rs 0/- | HERITGFOOD 2023-01-20 |
| 4 | 4 | Scheme Of Demerger | MANDHANA 2016-09-22 |
| 2 | 2 | Annual General Meeing | SHALPAINTS 2016-09-20 |
| 2 | 2 | Capital Reduction | MELSTAR 2024-08-16 |
| 2 | 2 | Composite Scheme Of Arrangement | CESC 2018-10-30 |
| 2 | 2 | Rights 1:1 @ Premium Rs 1/- | GLOBE 2024-02-23 |
| 2 | 2 | Rights 51:82 @ Premium Rs 0/- | GATECH 2025-04-28 |
| 2 | 2 | Scheme Of Amalgamation | IFGLREFRAC 2017-09-14 |
| 2 | 1 | Scheme Of Arangement- Bonus - 1 Debenture For 1 Equity Share Held | BRITANNIA 2019-08-22 |
| 2 | 2 | Scheme Of Arrangement & Reconstruction | 3PLAND 2016-02-11 |
| 1 | 1 | Annual Gemeral Meeting | TIRUMALCHM 2016-07-21 |
| 1 | 1 | Annual General Meeeting | REGENCERAM 2016-09-19 |
| 1 | 1 | Annual General Meeing/Ividend - Rs 6 Per Share | THERMAX 2017-07-27 |
| 1 | 1 | Annual General Meetin | HFCL 2017-09-15 |
| 1 | 1 | Annual General Meetingagm | UNITECH 2016-09-02 |
| 1 | 1 | Annual General Meteing | BBOX 2017-09-14 |
| 1 | 1 | Annual General Meting | PALREDTEC 2017-09-20 |
| 1 | 1 | Annual Genral Meeting | ANGIND 2016-09-16 |
| 1 | 1 | Annualgeneral Meeting | LCCINFOTEC 2017-12-20 |
| 1 | 1 | Bonus 17:25 | UEL 2025-05-30 |
| 1 | 1 | Bonus 1:1/Face Value Split (Sub-Division) - From Rs 10/- Per Share To Re 1/- Per Share | SUNILHITEC 2016-12-01 |
| 1 | 1 | Bonus 1:1/Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 2/- Per Share | BAJFINANCE 2016-09-08 |
| 1 | 1 | Bonus 1:1/Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 5/- Per Share | VEEDOL 2016-03-16 |
| 1 | 1 | Bonus 1:2/Face Value Split (Sub-Division) From Rs 10 Per Share To Rs 5 Per Share | HINDCOMPOS 2017-05-25 |
| 1 | 1 | Bonus 1:2/Face Value Split (Sub-Division) From Rs 2/- Per Share To Re 1/- Per Share | AVANTIFEED 2018-06-26 |
| 1 | 1 | Bonus 1:25/ Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 5/- Per Share | KTIL 2016-08-11 |
| 1 | 1 | Bonus 1:26 | INFINITE 2017-11-01 |
| 1 | 1 | Bonus 1:3/Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 5/- Per Share | SECURKLOUD 2016-10-10 |
| 1 | 1 | Bonus 1:5/Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 2/- Per Share | BEARDSELL 2017-05-04 |
| 1 | 1 | Bonus 25:202 | IGARASHI 2018-09-27 |
| 1 | 1 | Bonus 4:1/Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 5/- Per Share | RAMASTEEL 2016-03-14 |
| 1 | 1 | Bonus Ncrps 1:116 | TVSHLTD 2023-03-24 |
| 1 | 1 | Capital Reduction -  From Rs 10/- To Rs 4/- Per Share | GRANDFONRY 2016-03-21 |
| 1 | 1 | Capital Reduction Pursuant To Nclt Order | MAXIND 2022-07-26 |
| 1 | 1 | Capital Reduction Rs 10 To Rs 3.30 / Consolidation Rs 3.30 To Rs.10 | MONNETISPA 2018-08-29 |
| 1 | 1 | Composite Scheme Of Amalgamation And Arrangement | SABTN 2016-03-22 |
| 1 | 1 | Consolidation Of Equity Shares From Re 1 Per Share To Rs 10 Per Share | VERTOZ 2025-06-25 |
| 1 | 1 | De-Merger | TTML 2019-07-11 |
| 1 | 1 | Div - Rs 0.50 Per Sh | ASHAPURMIN 2021-09-21 |
| 1 | 1 | Extra-Ordinary General Meting | NEOGEN 2021-12-23 |
| 1 | 1 | Int Div - Rs 0.71 Per Sh | NHPC 2019-02-18 |
| 1 | 1 | Int Div - Rs 4/- Per Share (Purpose Revised) | COLPAL 2017-12-18 |
| 1 | 1 | Int Div -Rs 6 Per Sh | CYIENT 2018-10-30 |
| 1 | 1 | Int Div Re 0.40 Per Share | ADVANIHOTR 2017-02-07 |
| 1 | 1 | Int Div Re 1/- Per Share (Purpose Revised) | UNITEDTEA 2017-03-30 |
| 1 | 1 | Int Div Rs 4 Per Sh | TCS 2018-10-23 |
| 1 | 1 | Int Div- 2 Per Share (Purpose Revised) | HCLTECH 2018-08-02 |
| 1 | 1 | Int Div-Rs 0.5 Per Sh | SHREEPUSHK 2020-02-27 |
| 1 | 1 | Interim Div - Re 0.20 Per Share | SADBHIN 2018-11-26 |
| 1 | 1 | Interim Div - Rs 2.50 Per Share | MMFL 2019-02-22 |
| 1 | 1 | Interim Div - Rs 3 Per Share | MINDTREE 2018-10-25 |
| 1 | 1 | Interim Divdend | MOIL 2022-02-17 |
| 1 | 1 | Interim Divdend - Rs 2 Per Share | AEGISLOG 2022-02-17 |
| 1 | 1 | Interim Divdend - Rs 7.60 Per Share | CAMS 2021-02-17 |
| 1 | 1 | Interim Dividned - Rs 135 Per Share | NESTLEIND 2020-10-29 |
| 1 | 1 | Meeting Of Equity Shareholders | ACE 2018-06-14 |
| 1 | 1 | Merger/Demerger | MEGH 2021-05-18 |
| 1 | 1 | Rights  1:1 @ Premium Rs 4.50 Per Share | CNOVAPETRO 2016-10-24 |
| 1 | 1 | Rights - 4:25 Fully Paid Up Shares @ Premium Rs 500/- Per Share / 2:25 Partly Paid Up Shares @ Premium Rs 605/- Per Share | TATASTEEL 2018-01-31 |
| 1 | 1 | Rights 100:224 @ Premium Rs 20/- | JAIPURKURT 2024-07-04 |
| 1 | 1 | Rights 10:121@ Premium Rs 38/- | AVANTEL 2025-05-07 |
| 1 | 1 | Rights 10:21 @ Premium Rs 45/- | HCL-INSYS 2017-10-31 |
| 1 | 1 | Rights 10:211@ Premium Rs 135/- | SDBL 2023-04-13 |
| 1 | 1 | Rights 10:41 @ Premium Rs 220/- | SPANDANA 2025-07-24 |
| 1 | 1 | Rights 10:43 @ Premium Rs 22/- | BASML 2025-04-30 |
| 1 | 1 | Rights 10:51 @ Premium Rs 3/- | GREENPOWER 2024-08-13 |
| 1 | 1 | Rights 110:100 @ Premium Rs 1.75/- | SHAH 2022-12-23 |
| 1 | 1 | Rights 119:758 @ Premium Rs 218/- | HINDWAREAP 2024-10-25 |
| 1 | 1 | Rights 11: 50 @ Premium Rs 0/- | SEPC 2025-05-23 |
| 1 | 1 | Rights 11:10@ Premium Rs 4/- | SHREERAMA 2023-05-30 |
| 1 | 1 | Rights 11:30 @ Premium Rs 5/- | PRAXIS 2025-03-20 |
| 1 | 1 | Rights 11:5 @ Premium Rs 54/- | SICALLOG 2026-02-18 |
| 1 | 1 | Rights 11:64 @ Premium Rs 155/- | TIL 2026-03-23 |
| 1 | 1 | Rights 11:64 @ Premium Rs 473/- | CGCL 2023-02-17 |
| 1 | 1 | Rights 11:8 @ Premium Rs 0/- | TPHQ 2023-04-18 |
| 1 | 1 | Rights 11:8 @ Premium Rs 6.35/- | PRAXIS 2021-09-07 |
| 1 | 1 | Rights 11:83 @ Premium Rs 1298/- | PEL 2019-12-30 |
| 1 | 1 | Rights 12:25@ Premium Rs 0.60/- | VIKASECO 2021-11-24 |
| 1 | 1 | Rights 12:47 @ Premium Rs 5/- | SARVESHWAR 2025-08-22 |
| 1 | 1 | Rights 133:274 @ Premium Rs 40/- | KESORAMIND 2021-09-16 |
| 1 | 1 | Rights 13:10 @ Premium Rs 0.35/- | VIKASECO 2021-06-09 |
| 1 | 1 | Rights 13:100 @ Premium Rs 8/- | GVPTECH 2025-06-30 |
| 1 | 1 | Rights 13:118 @ Premium Rs 20/- | HCC 2024-03-15 |
| 1 | 1 | Rights 13:118 @ Premium Rs 308/- | BAJAJELEC 2020-02-05 |
| 1 | 1 | Rights 13:12 @ Premium Rs 20/- | VINEETLAB 2025-12-23 |
| 1 | 1 | Rights 13:20 @ Premium Rs 5/- | PRAXIS 2023-05-30 |
| 1 | 1 | Rights 13:25 @ Premium Rs 2.05/- | DAVANGERE 2025-08-06 |
| 1 | 1 | Rights 13:8 @ Premium Rs 0/- | AKSHAR 2024-08-23 |
| 1 | 1 | Rights 14:23 @ Premium Rs 13/- | MOKSH 2024-12-20 |
| 1 | 1 | Rights 14:25 @ Premium Rs 11/- | DHANBANK 2024-12-27 |
| 1 | 1 | Rights 14:29 @ Premium Rs 18.32/- | HILTON 2025-12-26 |
| 1 | 1 | Rights 15:32 @ Premium Rs 5.26/- | BHANDARI 2024-06-19 |
| 1 | 1 | Rights 15:7@ Premium Rs 490 Per Share | TATASTLLP 2019-06-24 |
| 1 | 1 | Rights 161:250 @ Premium Re 0.45 /- | ESSENTIA 2026-05-20 |
| 1 | 1 | Rights 16:47 @ Premium Rs 146/- | ARVINDFASN 2020-03-17 |
| 1 | 1 | Rights 17:70 @ Premium Rs 135/- | SHOPERSTOP 2020-11-19 |
| 1 | 1 | Rights 17:74@ Premium Rs 55 Per Share | LTF 2021-01-21 |
| 1 | 1 | Rights 18:91 @ Prem Rs 740 | KINGFA 2017-03-09 |
| 1 | 1 | Rights 19:100 @ Premium Rs 140/- | MAXIND 2025-04-29 |
| 1 | 1 | Rights 19:100 @ Premium Rs 45.70/- | TEXRAIL 2019-09-24 |
| 1 | 1 | Rights 19:29 @ Premium Rs 90/- | ASIANTILES 2021-09-08 |
| 1 | 1 | Rights 19:295 @ Premium Rs 205/- | SHANTIGOLD 2026-08-06 |
| 1 | 1 | Rights 19:41 @ Premium Rs 89/- | STALLION 2026-02-11 |
| 1 | 1 | Rights 19:62 @ Premium Rs 0/- | GREENPOWER 2023-08-18 |
| 1 | 1 | Rights 19:67 @ Premium Rs 215 Per Share | BHARTIARTL 2019-04-23 |
| 1 | 1 | Rights 1:1 | TFL 2022-11-04 |
| 1 | 1 | Rights 1:1 @ Premium Rs 1.30/- | SRPL 2023-07-06 |
| 1 | 1 | Rights 1:1 @ Premium Rs 11.25/- | JETFREIGHT 2023-01-11 |
| 1 | 1 | Rights 1:1 @ Premium Rs 15/- | SILGO 2024-02-22 |
| 1 | 1 | Rights 1:1 @ Premium Rs 20/- | ROML 2023-02-09 |
| 1 | 1 | Rights 1:1 @ Premium Rs 3/- | AJOONI 2024-05-07 |
| 1 | 1 | Rights 1:1 @ Premium Rs 4/- | CAPTRUST 2025-10-10 |
| 1 | 1 | Rights 1:1 @ Premium Rs 48/- | M&MFIN 2020-07-22 |
| 1 | 1 | Rights 1:1 @ Premium Rs 70 Per Share | 5PAISA 2019-05-28 |
| 1 | 1 | Rights 1:1 @ Premium Rs 90/- | RSWM 2022-12-16 |
| 1 | 1 | Rights 1:10 @ Prem Rs 197/- Per Share | CANBK 2017-02-17 |
| 1 | 1 | Rights 1:10 @ Premium Rs 193/- | SKIPPER 2024-01-12 |
| 1 | 1 | Rights 1:10 @ Premium Rs 315/- | SGIL 2024-09-11 |
| 1 | 1 | Rights 1:10 @ Premium Rs 78/- | HIRECT 2017-10-17 |
| 1 | 1 | Rights 1:10 @ Premium Rs 95/- | BHARATGEAR 2021-10-28 |
| 1 | 1 | Rights 1:11 @ Premium Rs 107.10/- | JTEKTINDIA 2025-07-25 |
| 1 | 1 | Rights 1:13@ Premium Rs 30/- | SDBL 2021-12-31 |
| 1 | 1 | Rights 1:14 @ Premium Rs 530/- | BHARTIARTL 2021-09-27 |
| 1 | 1 | Rights 1:15 @ Premium Rs 1247 | RELIANCE 2020-05-13 |
| 1 | 1 | Rights 1:16 @ Premium Rs 65/- | BROOKS 2023-07-28 |
| 1 | 1 | Rights 1:17 @ Premium Rs 14.50/- | LLOYDSENGG 2023-12-14 |
| 1 | 1 | Rights 1:17 @ Premium Rs 502/- | HCG 2026-03-02 |
| 1 | 1 | Rights 1:2 @ Premium Re 1.50/- | VCL 2023-07-24 |
| 1 | 1 | Rights 1:2 @ Premium Re 1/- | MITTAL 2024-10-03 |
| 1 | 1 | Rights 1:2 @ Premium Rs 1/- | GLOBE 2025-01-17 |
| 1 | 1 | Rights 1:2 @ Premium Rs 11/- | LIBAS 2022-09-15 |
| 1 | 1 | Rights 1:2 @ Premium Rs 148/- | SAMMAANCAP 2024-02-01 |
| 1 | 1 | Rights 1:2 @ Premium Rs 187/- | APCL 2022-12-16 |
| 1 | 1 | Rights 1:2 @ Premium Rs 290/- | 5PAISA 2026-03-17 |
| 1 | 1 | Rights 1:2 @ Premium Rs 5/- | ATALREAL 2024-08-22 |
| 1 | 1 | Rights 1:2 @ Premium Rs 54/- | SUVEN 2022-10-17 |
| 1 | 1 | Rights 1:2 @ Premium Rs 60/- Per Share | KTKBANK 2016-10-24 |
| 1 | 1 | Rights 1:2 @ Premium Rs 8/- | SANGINITA 2024-05-07 |
| 1 | 1 | Rights 1:20 @ Premium Rs. 440/- | DYNPRO 2022-05-12 |
| 1 | 1 | Rights 1:23 @ Premium Rs 2378/- | PEL 2018-01-31 |
| 1 | 1 | Rights 1:26 @ Premium Rs 817/- | TATACONSUM 2024-07-26 |
| 1 | 1 | Rights 1:27 @ Premium Rs 248/- | UNOMINDA 2020-08-14 |
| 1 | 1 | Rights 1:28 @ Prem Rs 67/- Per Share | ORIENTPPR 2016-11-18 |
| 1 | 1 | Rights 1:2@ Premium Rs 11.60/- | PATELENG 2023-02-06 |
| 1 | 1 | Rights 1:2@Prem Rs 40 | CREST 2016-09-15 |
| 1 | 1 | Rights 1:3 @ Premium Rs 112/- | LAKSHVILAS 2017-12-05 |
| 1 | 1 | Rights 1:3 @ Premium Rs 13/- Per Share | SOUTHBANK 2017-02-16 |
| 1 | 1 | Rights 1:3 @ Premium Rs 152/- | RUSHIL 2023-04-13 |
| 1 | 1 | Rights 1:3 @ Premium Rs 365/- | SOLARA 2024-05-15 |
| 1 | 1 | Rights 1:3 @ Premium Rs 40/- | RUSHIL 2020-09-10 |
| 1 | 1 | Rights 1:3 @ Premium Rs 5.06/- | SADHNANIQ 2024-09-13 |
| 1 | 1 | Rights 1:3 @ Premium Rs 8/- | BEARDSELL 2021-12-16 |
| 1 | 1 | Rights 1:30 @ Premium Rs 418/- | HATSUN 2022-12-07 |
| 1 | 1 | Rights 1:32 @ Premium Rs 90/- | GOKULAGRO 2023-03-08 |
| 1 | 1 | Rights 1:36 @ Premium Rs 3/- | SEPC 2023-11-28 |
| 1 | 1 | Rights 1:4 @ Premium Rs 1.33/- | INVENTURE 2024-07-05 |
| 1 | 1 | Rights 1:4 @ Premium Rs 21/- | SOUTHBANK 2024-02-27 |
| 1 | 1 | Rights 1:4 @ Premium Rs 24/- | VIPCLOTHNG 2017-11-17 |
| 1 | 1 | Rights 1:4 @ Premium Rs 282/- | MAHLIFE 2017-03-30 |
| 1 | 1 | Rights 1:4 @ Premium Rs 5.35/- | INDOWIND 2025-11-19 |
| 1 | 1 | Rights 1:4 @ Premium Rs 6/- | DUCON 2024-08-30 |
| 1 | 1 | Rights 1:4 @ Premium Rs 65/- | VALIANTLAB 2025-07-18 |
| 1 | 1 | Rights 1:4 @ Premium Rs 8/- | BAIDFIN 2025-11-17 |
| 1 | 1 | Rights 1:4@ Premium Rs 110/- | NGIL 2022-03-30 |
| 1 | 1 | Rights 1:5 @ Premium Rs 12.50/- | INDOWIND 2024-07-16 |
| 1 | 1 | Rights 1:5 @ Premium Rs 26/- | ARROWGREEN 2020-02-12 |
| 1 | 1 | Rights 1:5 @ Premium Rs 27.50/- | ABINFRA 2025-03-10 |
| 1 | 1 | Rights 1:5 @ Premium Rs 38/- | LLOYDSENT 2025-08-14 |
| 1 | 1 | Rights 1:5 @ Premium Rs 74/- | INDHOTEL 2017-10-04 |
| 1 | 1 | Rights 1:50 @ Premium Rs 175  With 6 Warrants For 50 Equity Shares | MOLDTKPAC 2020-10-21 |
| 1 | 1 | Rights 1:50 @ Premium Rs 690/- With 17 Warrants For 50 Equity Shares | SHAREINDIA 2023-02-28 |
| 1 | 1 | Rights 1:6 @ Premium Rs 215/- | COASTCORP 2022-08-25 |
| 1 | 1 | Rights 1:6 @ Premium Rs 33/- | IRISDOREME 2025-03-13 |
| 1 | 1 | Rights 1:6 @ Premium Rs 49/- | GEOJITFSL 2024-10-07 |
| 1 | 1 | Rights 1:6 @ Premium Rs 74/- | KARURVYSYA 2017-10-12 |
| 1 | 1 | Rights 1:7 @ Premium Rs 18/- | MGEL 2024-05-24 |
| 1 | 1 | Rights 1:7 @ Premium Rs 30/- | NGIL 2023-09-05 |
| 1 | 1 | Rights 1:7 @ Premium Rs 880/- | ASTEC 2025-07-04 |
| 1 | 1 | Rights 1:7 @ Premium Rs 95 Per Share | BHARATGEAR 2019-04-02 |
| 1 | 1 | Rights 1:8 @ Premium Rs 192/- | M&MFIN 2025-05-14 |
| 1 | 1 | Rights 1:8 @ Premium Rs 358/- | UPL 2024-11-26 |
| 1 | 1 | Rights 1:9 @ Premium 91 | RELTD 2026-06-08 |
| 1 | 1 | Rights 1:9 @ Premium Rs 149/- | INDHOTEL 2021-11-11 |
| 1 | 1 | Rights 1:9 @ Premium Rs 298/- | IIFL 2024-04-23 |
| 1 | 1 | Rights 20:119 @ Premium Rs 2.25/- | ESSENTIA 2024-05-31 |
| 1 | 1 | Rights 21:100 @ Premium Rs 76 Per Share | KREBSBIO 2019-01-31 |
| 1 | 1 | Rights 21:20@ Premium Rs 25/- | BASML 2021-09-08 |
| 1 | 1 | Rights 23:49 @ Premium Rs 181/- | DELPHIFX 2025-10-14 |
| 1 | 1 | Rights 23:49 @ Premium Rs 45/- | TSFINV 2021-04-26 |
| 1 | 1 | Rights 277:630 @ Premium Rs 11.50/- | HCC 2025-12-05 |
| 1 | 1 | Rights 27:47 | PATINTLOG 2021-02-17 |
| 1 | 1 | Rights 28:10 @ Premium Rs 0/- | TIL 2024-03-22 |
| 1 | 1 | Rights 29:30 @ Premium Rs 4/- | AJOONI 2022-11-25 |
| 1 | 1 | Rights 29:54@ Premium Rs 265/- | PNBHOUSING 2023-04-05 |
| 1 | 1 | Rights 29:60 @ Premium Rs 6.68/- | HILTON 2026-02-24 |
| 1 | 1 | Rights 2:1 @ Premium Rs 0/- | AURIGROW 2023-05-12 |
| 1 | 1 | Rights 2:1 @ Premium Rs 11/- | BALKRISHNA 2024-03-15 |
| 1 | 1 | Rights 2:1 @ Premium Rs 2/- | AKG 2022-12-16 |
| 1 | 1 | Rights 2:11 @ Premium Rs 44/- | MAGNUM 2024-01-25 |
| 1 | 1 | Rights 2:15 @ Premium Rs 1390/- | THANGAMAYL 2025-02-11 |
| 1 | 1 | Rights 2:15 @ Premium Rs 70/- | SPENCERS 2020-07-28 |
| 1 | 1 | Rights 2:17 @ Premium Rs 545/- | AARTISURF 2023-01-17 |
| 1 | 1 | Rights 2:23 @ Premium Rs 347/- | KILITCH 2025-07-15 |
| 1 | 1 | Rights 2:3 | SIGMAADV 2021-07-12 |
| 1 | 1 | Rights 2:3 @ Premium Rs 40/- | VSSL 2017-04-07 |
| 1 | 1 | Rights 2:5 @ Premium Re 0.85/- | VIKASLIFE 2021-05-20 |
| 1 | 1 | Rights 2:5 @ Premium Rs 1.17/- | KSHITIJPOL 2026-08-19 |
| 1 | 1 | Rights 2:5 @ Premium Rs 290/- | NDLVENTURE 2021-10-22 |
| 1 | 1 | Rights 2:5 @ Premium Rs 45/- | HILTON 2022-10-20 |
| 1 | 1 | Rights 2:5 @ Premium Rs 5.80/- | CYBERMEDIA 2025-08-01 |
| 1 | 1 | Rights 2:53 @ Premium Rs 0/- | SEPC 2023-03-29 |
| 1 | 1 | Rights 2:5@ Premium Rs 2/- | INDOWIND 2023-01-13 |
| 1 | 1 | Rights 2:7 | JMCPROJECT 2016-01-11 |
| 1 | 1 | Rights 2:7 @ Premium Rs 22/- | TEXRAIL 2021-10-21 |
| 1 | 1 | Rights 2:7 @ Premium Rs 29/- | PRICOLLTD 2020-11-24 |
| 1 | 1 | Rights 2:9 @ Premium Rs 16/- | SHIVAMAUTO 2021-12-09 |
| 1 | 1 | Rights 2:9 @ Premium Rs 7/- | 3IINFOLTD 2025-09-26 |
| 1 | 1 | Rights 300:167 @ Premium Rs 5/- | ONELIFECAP 2026-02-16 |
| 1 | 1 | Rights 33:13@ Premium Rs 0.80/- | ESSENTIA 2022-05-04 |
| 1 | 1 | Rights 33:98 @ Premium Rs 24.30/- | SAKUMA 2024-04-15 |
| 1 | 1 | Rights 36:311 @ Premium Rs 3.86 | SHAH 2026-05-27 |
| 1 | 1 | Rights 37:200 @ Premium Rs 6/- | ESSENTIA 2022-11-17 |
| 1 | 1 | Rights 3:1 @ Premium Rs 0/- | CALSOFT 2025-01-15 |
| 1 | 1 | Rights 3:10 @ Premium Rs 50/- | SILGO 2026-01-05 |
| 1 | 1 | Rights 3:10 @ Premium Rs 88/- | SIKKO 2024-12-06 |
| 1 | 1 | Rights 3:10@ Premium Rs 220 Per Share | WOCKPHARMA 2022-03-08 |
| 1 | 1 | Rights 3:14 @ Premium Rs 9/- | ONIDA 2025-06-30 |
| 1 | 1 | Rights 3:16 @ Premium Rs 238/- | DHANI 2018-02-09 |
| 1 | 1 | Rights 3:19 @ Premium Rs 18/- | ATL 2025-11-14 |
| 1 | 1 | Rights 3:2 @ Premium Re 1/- | ORIENTALTL 2024-09-05 |
| 1 | 1 | Rights 3:2 @ Premium Re. 0.63/- | GANGAFORGE 2026-07-02 |
| 1 | 1 | Rights 3:2 @ Premium Rs 15/- | NAGREEKEXP 2024-01-30 |
| 1 | 1 | Rights 3:2 @ Premium Rs 5/- | ADROITINFO 2024-01-19 |
| 1 | 1 | Rights 3:2 @ Premium Rs 62.50/- | SHALPAINTS 2018-11-06 |
| 1 | 1 | Rights 3:2 @ Premium Rs 75/- | AURUM 2022-04-12 |
| 1 | 1 | Rights 3:20 @ Premium Rs 123/- | DEEPAKFERT 2020-09-16 |
| 1 | 1 | Rights 3:20 @ Premium Rs 131/- | ARVINDFASN 2021-02-23 |
| 1 | 1 | Rights 3:20 @ Premium Rs 133/- | EXICOM 2025-07-07 |
| 1 | 1 | Rights 3:25 @ Premium Rs 1799/- | ADANIENT 2025-11-17 |
| 1 | 1 | Rights 3:26 @ Premium Rs 3.50/- | BHANDARI 2023-09-22 |
| 1 | 1 | Rights 3:26 @ Premium Rs 560/- | SHRIRAMFIN 2020-07-09 |
| 1 | 1 | Rights 3:4 @ Premium Rs 78/- | NDTV 2025-09-12 |
| 1 | 1 | Rights 3:5 @ Premium Rs 20/- | RPPINFRA 2021-09-17 |
| 1 | 1 | Rights 3:5 @ Premium Rs 38/- | SHRADHA 2025-09-16 |
| 1 | 1 | Rights 3:5 @ Premium Rs 45/- | GENESYS 2026-08-06 |
| 1 | 1 | Rights 3:7 @ Premium Rs 14/- | SUMEETINDS 2017-12-15 |
| 1 | 1 | Rights 3:7 @ Premium Rs 5/- | DIL 2023-06-01 |
| 1 | 1 | Rights 3:8 @ Premium Rs 247/- | MAHLIFE 2025-05-23 |
| 1 | 1 | Rights 3:8 @ Premium Rs 267/- | MAHLOG 2025-07-23 |
| 1 | 1 | Rights 45:301 @ Premium Rs 290/- | KRISHIVAL 2025-12-17 |
| 1 | 1 | Rights 48:125 @ Premium Rs 50/- | SATIN 2020-08-04 |
| 1 | 1 | Rights 49:100 @ Premium Rs 9/- | HCC 2018-11-20 |
| 1 | 1 | Rights 4:10 @ Premium Rs 15/- | NGIL 2024-05-30 |
| 1 | 1 | Rights 4:21 @ Premium Rs 1.80/- | VIKASLIFE 2021-10-29 |
| 1 | 1 | Rights 4:27 @ Premium Rs 11/- | TTL 2025-07-04 |
| 1 | 1 | Rights 4:27 @ Premium Rs 62/- | GDL 2020-07-23 |
| 1 | 1 | Rights 4:43@ Premium Rs 1790/- | ETHOSLTD 2025-06-12 |
| 1 | 1 | Rights 4:5 @ Premium Rs 1.56/- | BHANDARI 2026-02-25 |
| 1 | 1 | Rights 4:5 @ Premium Rs 14/- | UDAICEMENT 2023-06-14 |
| 1 | 1 | Rights 4:5 @ Premium Rs 4.40/- | KSHITIJPOL 2024-06-18 |
| 1 | 1 | Rights 4:9 @ Premium Rs 7/- | BTML 2025-03-24 |
| 1 | 1 | Rights 50:189 @ Premium Rs 152/- | UGROCAP 2025-06-05 |
| 1 | 1 | Rights 55:91 @ Premium Rs 121/- | FUSION 2025-04-04 |
| 1 | 1 | Rights 588:1000@ Premium Rs 2/- | LGBFORGE 2019-01-03 |
| 1 | 1 | Rights 5: 116 At Premium Rs 244/- Per Share | SPARC 2016-03-16 |
| 1 | 1 | Rights 5:14 @ Premium Rs 143/- | PRABHA 2026-03-11 |
| 1 | 1 | Rights 5:14 @ Premium Rs 72/- | CAPTRUST 2025-06-18 |
| 1 | 1 | Rights 5:14@ Premium Rs 35/- | REFEX 2020-06-16 |
| 1 | 1 | Rights 5:21 @ Premium Rs 3/- | SUZLON 2022-10-03 |
| 1 | 1 | Rights 5:22 @ Premium Rs 81/- | INTELLECT 2017-07-17 |
| 1 | 1 | Rights 5:24 @ Premium Rs 9/- | AVONMORE 2024-12-12 |
| 1 | 1 | Rights 5:31 @ Premium Rs 75.70/- | NACLIND 2025-12-12 |
| 1 | 1 | Rights 5:41 @ Premium Rs 109/- | CAMLINFINE 2025-01-08 |
| 1 | 1 | Rights 5:46 @ Premium Rs 71/- | PPLPHARMA 2023-08-02 |
| 1 | 1 | Rights 5:78 @ Premium Rs 110/- | INOXWIND 2025-07-29 |
| 1 | 1 | Rights 613:399 | PATINTLOG 2021-10-28 |
| 1 | 1 | Rights 67:267 @ Premium Rs 9/- | CCAVENUE 2025-06-26 |
| 1 | 1 | Rights 67:66 @ Premium Rs 51/- | MAXVIL 2018-06-21 |
| 1 | 1 | Rights 6:179 @ Premium Rs 1810/- | GRASIM 2024-01-10 |
| 1 | 1 | Rights 6:19 @ Premium Rs 66/- | MITCON 2024-06-20 |
| 1 | 1 | Rights 6:32 @ Premium Rs 138/- | SHALPAINTS 2017-12-28 |
| 1 | 1 | Rights 6:37 @ Premium Rs 13/- | JYOTISTRUC 2024-03-21 |
| 1 | 1 | Rights 6:47 @ Premium Rs 1641/- | SOBHA 2024-06-19 |
| 1 | 1 | Rights 6:55 @ Premium Rs 3 | SEPC 2024-06-25 |
| 1 | 1 | Rights 7:10 @ Premium Rs 34.80/- | MARSHALL 2023-09-28 |
| 1 | 1 | Rights 7:10 @ Prm Rs 102/- | VHLTD 2024-11-29 |
| 1 | 1 | Rights 7:23 @ Premium Rs 5/- | VARDMNPOLY 2024-08-28 |
| 1 | 1 | Rights 7:40 @ Premium Rs 26/- | PATELENG 2025-12-04 |
| 1 | 1 | Rights 7:5 @ Premium Rs 8/- Per Share | PATELENG 2019-09-17 |
| 1 | 1 | Rights 7:71 @ Premium Rs 4/- | URJA 2021-01-14 |
| 1 | 1 | Rights 7:75 @ Premium Rs 220/- | KDDL 2021-03-30 |
| 1 | 1 | Rights 7:9 @ Premium Rs 0/- | KEEPLEARN 2024-05-14 |
| 1 | 1 | Rights 7:94 @ Premium Rs 774/- | PVRINOX 2020-07-09 |
| 1 | 1 | Rights 87:38 @ Premium Of Rs 2.50 Per Share | IDEA 2019-03-29 |
| 1 | 1 | Rights 8:1 @ Premium Rs 0/- | SADHNANIQ 2026-02-18 |
| 1 | 1 | Rights 8:103 @ Premium Rs 148/- | EFCIL 2026-05-07 |
| 1 | 1 | Rights 8:103 @ Premium Rs 8/- | PATINTLOG 2024-09-06 |
| 1 | 1 | Rights 8:11 @ Premium Re 0.50/- | VIJIFIN 2024-05-15 |
| 1 | 1 | Rights 8:13 @ Premium Rs 4/- | UTKARSHBNK 2025-10-14 |
| 1 | 1 | Rights 8:25 @ Premium Rs 18/- | COMPINFO 2022-11-14 |
| 1 | 1 | Rights 8:25 @ Premium Rs 9.86/- | SUMEETINDS 2026-06-12 |
| 1 | 1 | Rights 8:33 @ Premium Rs 135/- | AVG 2026-05-21 |
| 1 | 1 | Rights 8:85 @ Premium Rs 63/- | EIHOTEL 2020-09-22 |
| 1 | 1 | Rights 9:10 @ Premium Rs 8/- | NECCLTD 2023-06-02 |
| 1 | 1 | Rights 9:20 @ Premium Rs 10/- | BROOKS 2020-02-11 |
| 1 | 1 | Rights 9:25 @ Premium Rs 90/- | TEMBO 2022-08-08 |
| 1 | 1 | Rights 9:26 @ Premium Rs 14/- | JYOTISTRUC 2025-02-10 |
| 1 | 1 | Rights 9:34 @ Premium Rs 31/- | LLOYDSENGG 2025-04-28 |
| 1 | 1 | Rights 9:5 @ Premium Rs 5/- | NARMADA 2024-09-13 |
| 1 | 1 | Rights 9:77 Partly Paid @ Premium Rs 100/- | ABFRL 2020-06-30 |
| 1 | 1 | Rights Issue 30:37@ Premium Rs 53/- | ASIANTILES 2022-04-11 |
| 1 | 1 | Rights Issue 4:17@ Premium Rs 390/- | BHAGCHEM 2022-04-07 |
| 1 | 1 | Rights:14 Compulosry Convertible Debentures For Every 15 Equity Shares | ZUARI 2019-09-13 |
| 1 | 1 | Scheme Of Arrangement - Bonus Ncrps 1:10 | RADIOCITY 2023-01-13 |
| 1 | 1 | Scheme Of Arrangement - Bonus Ncrps 4:1 | TVSMOTOR 2025-08-25 |
| 1 | 1 | Scheme Of Arrangement In The Nature Of Demerger | MOHITIND 2016-03-30 |
| 1 | 1 | Scheme Of Arrangement Of Demerger | VIKASECO 2018-11-19 |
| 1 | 1 | Sheme Of Arrangement | STLTECH 2016-06-15 |

## Parsed Split And Bonus Purposes

| Category | Count | Purpose | Price Factor | Volume Factor | First Example |
| --- | ---: | --- | ---: | ---: | --- |
| BONUS | 1 | Annual General Meeting/Dividend - Rs 2.50 Per Share/Bonus 1:10 (Revised) | 0.9090909091 | 1.1000000000 | ICICIBANK 2017-06-20 |
| BONUS | 1 | Bonus  1:4 | 0.8000000000 | 1.2500000000 | RITES 2019-08-08 |
| BONUS | 2 | Bonus 10:1 | 0.0909090909 | 11.0000000000 | VSTIND 2024-09-06 |
| BONUS | 1 | Bonus 13:10 | 0.4347826087 | 2.3000000000 | VINNY 2023-02-24 |
| BONUS | 1 | Bonus 1: 1 | 0.5000000000 | 2.0000000000 | MAANALU 2021-08-02 |
| BONUS | 1 | Bonus 1: 2 | 0.6666666667 | 1.5000000000 | ONGC 2016-12-15 |
| BONUS | 181 | Bonus 1:1 | 0.5000000000 | 2.0000000000 | MINDTREE 2016-03-09 |
| BONUS | 1 | Bonus 1:1 /Dividend- Rs 29 Per Share | 0.5000000000 | 2.0000000000 | TCS 2018-05-31 |
| BONUS | 1 | Bonus 1:1/ Dividend- Rs 5 Per Share | 0.5000000000 | 2.0000000000 | NIACL 2018-06-27 |
| BONUS | 1 | Bonus 1:1/Dividend- Rs 13.5 Per Share | 0.5000000000 | 2.0000000000 | GICRE 2018-07-12 |
| BONUS | 1 | Bonus 1:1/Dividend- Rs 7 Per Share | 0.5000000000 | 2.0000000000 | EMAMILTD 2018-06-21 |
| BONUS | 1 | Bonus 1:1/Interim Dividend Rs 2/- Per Share (Purpose Revised) | 0.5000000000 | 2.0000000000 | ORBTEXP 2017-02-14 |
| BONUS | 12 | Bonus 1:10 | 0.9090909091 | 1.1000000000 | MUTHOOTCAP 2017-06-12 |
| BONUS | 66 | Bonus 1:2 | 0.6666666667 | 1.5000000000 | KOTHARIPRO 2016-01-05 |
| BONUS | 1 | Bonus 1:2/ Dividend - Rs 1.10 Per Share | 0.6666666667 | 1.5000000000 | HINDPETRO 2017-07-11 |
| BONUS | 18 | Bonus 1:3 | 0.7500000000 | 1.3333333333 | VIVIDHA 2016-03-30 |
| BONUS | 15 | Bonus 1:4 | 0.8000000000 | 1.2500000000 | GMBREW 2016-05-30 |
| BONUS | 11 | Bonus 1:5 | 0.8333333333 | 1.2000000000 | MENONBE 2016-08-30 |
| BONUS | 1 | Bonus 1:7 | 0.8750000000 | 1.1428571429 | DPWIRES 2023-11-08 |
| BONUS | 35 | Bonus 2:1 | 0.3333333333 | 3.0000000000 | HINDPETRO 2016-09-14 |
| BONUS | 1 | Bonus 2:1/Dividend- Rs 1.60 Per Share | 0.3333333333 | 3.0000000000 | UNOMINDA 2018-07-11 |
| BONUS | 1 | Bonus 2:3 | 0.6000000000 | 1.6666666667 | BCG 2022-03-15 |
| BONUS | 10 | Bonus 2:5 | 0.7142857143 | 1.4000000000 | HATSUN 2016-07-13 |
| BONUS | 1 | Bonus 2:9 | 0.8181818182 | 1.2222222222 | SADHNANIQ 2023-07-05 |
| BONUS | 13 | Bonus 3:1 | 0.2500000000 | 4.0000000000 | BALMLAWRIE 2016-12-26 |
| BONUS | 1 | Bonus 3:2 | 0.4000000000 | 2.5000000000 | NAVKARURB 2025-04-24 |
| BONUS | 1 | Bonus 3:4 | 0.5714285714 | 1.7500000000 | TIRUPATIFL 2021-10-07 |
| BONUS | 13 | Bonus 4:1 | 0.2000000000 | 5.0000000000 | DHARAN 2021-08-12 |
| BONUS | 1 | Bonus 4:10 | 0.7142857143 | 1.4000000000 | MAGADSUGAR 2019-06-27 |
| BONUS | 1 | Bonus 4:5 | 0.5555555556 | 1.8000000000 | NINSYS 2023-08-03 |
| BONUS | 5 | Bonus 5:1 | 0.1666666667 | 6.0000000000 | ABMINTLTD 2017-03-15 |
| BONUS | 1 | Bonus 5:7 | 0.5833333333 | 1.7142857143 | RMDRIP 2026-04-10 |
| BONUS | 1 | Bonus 6:11 | 0.6470588235 | 1.5454545455 | LAL 2024-03-28 |
| BONUS | 1 | Bonus 7:5 | 0.4166666667 | 2.4000000000 | LGHL 2025-10-10 |
| BONUS | 1 | Bonus 9:1 | 0.1000000000 | 10.0000000000 | SKYGOLD 2024-12-16 |
| BONUS | 1 | Bonus- 1:2 | 0.6666666667 | 1.5000000000 | AJANTPHARM 2022-06-22 |
| SPLIT | 1 | Annual General Meeting/Dividend - Rs 10 Per Share/Face Value Split (Sub-Division) - From Rs 10/- Per Share To Re 1/- Per Share (Purpose Revised) | 0.1000000000 | 10.0000000000 | DWARKESH 2017-08-10 |
| SPLIT | 1 | Annual General Meeting/Face Value Split (Sub-Division) - From Rs 10/- Per Share To Re 1/- Per Share | 0.1000000000 | 10.0000000000 | CCAVENUE 2017-08-31 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 10 /- Per Share To Rs 2/- Per Share | 0.2000000000 | 5.0000000000 | ZENSARTECH 2018-09-07 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 10 Per Share To Re 1 Per Share | 0.1000000000 | 10.0000000000 | TTKPRESTIG 2021-12-14 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 10 Per Share To Rs 2 Per Share | 0.2000000000 | 5.0000000000 | MARINE 2021-02-18 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 10 Per Share To Rs 5  Per Share | 0.5000000000 | 2.0000000000 | MOTOGENFIN 2020-06-19 |
| SPLIT | 92 | Face Value Split (Sub-Division) - From Rs 10/- Per Share To Re 1/- Per Share | 0.1000000000 | 10.0000000000 | PRAKASHSTL 2016-03-03 |
| SPLIT | 4 | Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 1/- Per Share | 0.1000000000 | 10.0000000000 | TRIDENT 2019-12-13 |
| SPLIT | 115 | Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 2/- Per Share | 0.2000000000 | 5.0000000000 | VIVIMEDLAB 2016-04-06 |
| SPLIT | 56 | Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 5/- Per Share | 0.5000000000 | 2.0000000000 | MOLDTKPAC 2016-02-17 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 2 Per Share To Rs 1 Per Share | 0.5000000000 | 2.0000000000 | HDFCBANK 2019-09-19 |
| SPLIT | 31 | Face Value Split (Sub-Division) - From Rs 2/- Per Share To Re 1/- Per Share | 0.5000000000 | 2.0000000000 | AMRUTANJAN 2018-04-13 |
| SPLIT | 2 | Face Value Split (Sub-Division) - From Rs 2/- Per Share To Rs 1/- Per Share | 0.5000000000 | 2.0000000000 | SUNTECK 2017-07-25 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 3/- Per Share To Re 1/- Per Share | 0.3333333333 | 3.0000000000 | ESSENTIA 2022-02-03 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 4/- Per Share To Re 1/- Per Share | 0.2500000000 | 4.0000000000 | PILITA 2016-08-24 |
| SPLIT | 2 | Face Value Split (Sub-Division) - From Rs 4/- Per Share To Rs 2/- Per Share | 0.5000000000 | 2.0000000000 | SPLPETRO 2023-01-06 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 5 Per Share To Rs 2 Per Share | 0.4000000000 | 2.5000000000 | APCOTEXIND 2019-07-04 |
| SPLIT | 19 | Face Value Split (Sub-Division) - From Rs 5/- Per Share To Re 1/- Per Share | 0.2000000000 | 5.0000000000 | GREENPLY 2016-01-06 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 5/- Per Share To Re 2/- Per Share | 0.4000000000 | 2.5000000000 | VEEDOL 2021-07-26 |
| SPLIT | 10 | Face Value Split (Sub-Division) - From Rs 5/- Per Share To Rs 2/- Per Share | 0.4000000000 | 2.5000000000 | ALKYLAMINE 2021-05-11 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs 6/- Per Share To Re 1/- Per Share | 0.1666666667 | 6.0000000000 | ALMONDZ 2024-07-23 |
| SPLIT | 1 | Face Value Split (Sub-Division) - From Rs10/- Per Share To Re 1/- Per Share | 0.1000000000 | 10.0000000000 | NESTLEIND 2024-01-05 |
| SPLIT | 2 | Face Value Split (Sub-Division) - From Rs10/- Per Share To Rs 5/- Per Share | 0.5000000000 | 2.0000000000 | PGIL 2024-01-05 |
| SPLIT | 3 | Face Value Split From Rs 10 To Re 1 | 0.1000000000 | 10.0000000000 | VGUARD 2016-08-30 |
| SPLIT | 1 | Face Value Split From Rs 10 To Re 2 | 0.2000000000 | 5.0000000000 | GRASIM 2016-10-06 |
| SPLIT | 3 | Face Value Split From Rs 10 To Rs 2 | 0.2000000000 | 5.0000000000 | LUXIND 2016-06-06 |
| SPLIT | 2 | Face Value Split From Rs 10/- Per Share To Re 1/- Per Share | 0.1000000000 | 10.0000000000 | BEL 2017-03-16 |
| SPLIT | 4 | Face Value Split From Rs 10/- Per Share To Rs 2/- Per Share | 0.2000000000 | 5.0000000000 | GAYAPROJ 2017-02-10 |
| SPLIT | 2 | Face Value Split From Rs 2 To Re 1 | 0.5000000000 | 2.0000000000 | JMTAUTOLTD 2016-09-21 |
| SPLIT | 3 | Fv Splt Frm Rs 10 To Re 1 | 0.1000000000 | 10.0000000000 | VIJIFIN 2016-10-25 |
| SPLIT | 7 | Fv Splt Frm Rs 10 To Rs 2 | 0.2000000000 | 5.0000000000 | SOLARINDS 2016-07-13 |
| SPLIT | 2 | Fv Splt Frm Rs 10 To Rs 5 | 0.5000000000 | 2.0000000000 | BHAGERIA 2016-10-26 |
| SPLIT | 1 | Fv Splt Frm Rs 2 To Re 1 | 0.5000000000 | 2.0000000000 | ALANKIT 2016-12-15 |
| SPLIT | 1 | Fv Splt Frm Rs 5 To Re 1 | 0.2000000000 | 5.0000000000 | GULPOLY 2016-12-27 |
| SPLIT | 1 | Interim Div - Rs 6/- Per Share + Face Value Split (Sub-Division) - From Rs 10/- Per Share To Re 1/- Per Share | 0.1000000000 | 10.0000000000 | WELSPUNLIV 2016-03-21 |

## Row-Level Failures

None.

## Interpretation

This report is a corpus scan, not a universe freeze. It identifies the
full-window corporate-action vocabulary that the V0 parser can and cannot
classify deterministically. Universe selection must still apply D-021 to
candidate symbols over this same window.
