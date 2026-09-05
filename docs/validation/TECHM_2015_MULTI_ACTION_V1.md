# TECHM 2015 Multi-Action Data Validation V1

**Date:** 2026-09-05
**Methodology:** `DATA_METHODOLOGY_V1_D078`
**Status:** PASS - source replay and deterministic adjustment

## Scope

This check uses TECHM's 18, 19, and 20 March 2015 NSE EQ bars and the saved NSE
corporate-action row. No strategy signal, portfolio, P&L, research-period
diagnosis, or holdout output is computed. This is not a full warm-up dataset
build. B006 remains CANCELLED and no C001 experiment is registered.

## Entitlement Evidence

The issuer's [2014-15 annual report](https://cache.techmahindra.com/cache/investors/Annual-Report-FY14-15.pdf),
PDF page 98 (printed page 97), records the bonus and split terms and share
allotments. The 1:1 equity bonus doubles shares; the Rs 10 to Rs 5 split doubles
them again. Four final shares per original share implies historical price
factor `0.25` and volume factor `4`.

The saved NSE action record states:

```text
symbol: TECHM
series: EQ
exDate: 19-Mar-2015
recDate: 20-Mar-2015
subject: Bonus 1:1 / Face Value Split - From Rs 10/- Per Share To Rs 5/- Per Share
```

The source row is retained in the
[committed fixture](../../tests/fixtures/techm_2015_multi_action.json).
The full local 2015 corporate-action source file has SHA-256
`70943398f7a457fd54eeffea3bc9250b6dce3c2f9c0108ce0ff9d7d24bd6df96`.
It is the original input behind the committed
[B006 warm-up scan](B006_CORPORATE_ACTION_WARMUP_SCAN_V0.md), not a regenerated
or edited historical artifact.

## Raw Archive Identity

| Session | Official NSE archive | SHA-256 |
| --- | --- | --- |
| 2015-03-18 | [cm18MAR2015bhav.csv.zip](https://nsearchives.nseindia.com/content/historical/EQUITIES/2015/MAR/cm18MAR2015bhav.csv.zip) | `5fbd5bbac0a5bd9e509a439fb5fef7c997934e4a89e67fa6563e4a4d842e1997` |
| 2015-03-19 | [cm19MAR2015bhav.csv.zip](https://nsearchives.nseindia.com/content/historical/EQUITIES/2015/MAR/cm19MAR2015bhav.csv.zip) | `da295c74d69cd74e2df4e33a356913a4fdae654c7dd84df98280d3a8c2212858` |
| 2015-03-20 | [cm20MAR2015bhav.csv.zip](https://nsearchives.nseindia.com/content/historical/EQUITIES/2015/MAR/cm20MAR2015bhav.csv.zip) | `d876d3d801afc7c3c315d319f9e96c55f64ab4dfc32074377ca9f2c0a6554271` |

All three archives parse with zero rejected EQ rows. The replay compares the
date, unique TECHM row, ISIN, OHLC, volume, and previous close with the fixture.
Raw archives remain local immutable inputs, outside the committed strategy
datasets. Hash mismatches or source-row differences fail the replay.

## Adjustment Check

| Date | Raw close | Price factor | Adjusted close | Raw volume | Volume factor | Adjusted volume |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2015-03-18 | 2800.50 | 0.25 | 700.125000 | 3806886 | 4 | 15227544.000000 |
| 2015-03-19 | 687.15 | 1 | 687.150000 | 5621879 | 1 | 5621879.000000 |
| 2015-03-20 | 678.30 | 1 | 678.300000 | 3616042 | 1 | 3616042.000000 |

Pre-event adjusted open/high/low are `718.500000 / 720.000000 / 697.500000`.
The ex-date open is `695.000000`. The remaining market price movement is
retained; continuity does not mean forcing adjacent prices to equality.
The factor comes from the entitlement, not a fitted price ratio.

NSE's ex-date PREVCLOSE remains the unadjusted `2800.50`; it is not an
independent exchange-adjusted reference price. The fixture preserves it as
source metadata and does not infer the factor from that field.

The ISIN remains `INE669C01028` on 19 March and changes to `INE669C01036` on
20 March, the record date. The existing record-date identifier rule explains
this change. Both dates are preserved; only the ex-date sets the adjustment
boundary. A test removing the record date correctly causes an ISIN error.

## Reproduction And Limits

The [offline replay script](../../scripts/validate_techm_multi_action.py)
does not download anything or accept an arbitrary strategy date range. With
the hash-matching inputs already acquired locally, the command used was:

```powershell
.\.venv\Scripts\python.exe scripts\validate_techm_multi_action.py --raw-root work\data_methodology_v1\raw --corporate-action-source work\b006_corporate_actions_warmup_2015_rows.json --output docs\validation\TECHM_2015_MULTI_ACTION_V1.json
```

The [machine-readable result](TECHM_2015_MULTI_ACTION_V1.json) records the
source hashes, per-component factors, and adjusted rows. Its
`fixture_canonical_sha256` is SHA-256 of the fixture parsed as JSON and encoded
using sorted keys, compact separators, and ASCII escaping. This avoids
changing fixture identity merely because Windows and Linux use different
line endings. Raw-source hashes remain exact byte hashes.

The committed fixture can be tested offline without the local archives. Full
source replay additionally requires the exact original corpus snapshot and
three archives; a fresh endpoint response may have a different hash and must
not silently replace this evidence.

This validation establishes the implemented mechanical treatment of this
event. It does not validate every combined corporate event, a future C001
dataset, or any investment hypothesis. Unknown or conflicting records remain
quarantined, and the frozen V0 pipeline retains its original parser.
