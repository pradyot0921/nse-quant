# Corporate-Action Adjustment Notes

**Status:** Phase 1 implementation note  
**Decision anchor:** D-016, D-017, D-018, D-019, and D-020 in `docs/DECISIONS.md`

## V1 Supported Actions

The first corporate-action parser supports only deterministic single-event actions:

- stock splits where the purpose text contains an old face value and a new face value;
- bonus issues where the purpose text contains exactly one colon-separated ratio.

Real NSE split wording includes `Per Share` between each face value and the
`To` separator. That form is supported explicitly.

## Ignored No-Op Actions

Some recognised corporate-action records do not require an OHLCV adjustment for V1. These parse as `IGNORED`, not `UNSUPPORTED`:

- dividends;
- AGMs / EGMs;
- board meetings;
- name changes;
- buybacks.

These records keep price and volume factors at 1. They must be explicit known no-ops, not a catch-all for text the parser does not understand.

`Buy Back` records are ignored for price and volume adjustment because tender-offer and open-market buybacks do not multiply or dilute the holdings of non-participating shareholders.

## Unsupported Actions

Unknown, ambiguous, or price-continuity-affecting events that V1 does not support parse as `UNSUPPORTED` and must be quarantined for manual review before downstream data is trusted.

Unsupported or ambiguous events affecting a frozen-universe symbol during the research window must halt or quarantine dataset construction. Logging and continuing with an unadjusted series is not acceptable.

The ingestion/data-build layer must call `validate_actions()` once for the target symbols and research date range before factor lookup or adjusted data construction. `factors_for_date()` is a pure lookup that assumes the input has already passed validation.

Any purpose string containing `Scheme Of Arrangement` is unsupported in V1,
even when it also contains split or bonus language. A scheme is a corporate
reorganisation and is not safe to reduce to one mechanical split or equity-bonus
factor.

Rights issues remain unsupported in V0. A symbol with a rights issue inside the research window is excluded from the frozen V0 universe unless a later decision adds deterministic rights adjustment support.

UDiFF row-level ISIN changes are an independent validation signal. If a symbol's ISIN changes from the prior session and there is no same-date corporate-action record of any type, the loader must halt or quarantine the symbol/date as a possible missing corporate action.

## Ambiguous Or Combined Events

A single NSE purpose string that contains both a split and a bonus is unsupported in V1.

The current parser returns one `ParsedCorporateAction`, so it cannot safely represent two actions on the same ex-date. Until the model supports multiple parsed events from one source record, combined split-plus-bonus text must quarantine instead of silently dropping one action.

## Bonus Ratio Parsing

Bonus ratios use a colon separator. Slash-separated tokens are not accepted as bonus ratios because they collide with dates in NSE purpose text.

If more than one colon-shaped ratio token appears in the purpose text, the record is unsupported. The parser must not pick the first ratio and continue.

Bonus ratios are interpreted as new shares per existing shares. Official NSE CM-UDiFF checks confirmed this convention on PATANJALI `Bonus 2:1` on 11 September 2025.

Bonus issues of non-equity instruments are unsupported. This includes
debentures, preference shares, NCRPS, NCDs, CRPS, OCRPS, and warrants.

## Adjustment Precision

Corporate-action factors are `Decimal` values quantized to 10 decimal places using `ROUND_HALF_UP`.

Adjusted OHLC prices are quantized to `Decimal("0.000001")` rupees after applying cumulative factors. Adjusted volume is adjusted alongside price and quantized to six decimal places.

Final accounting and NAV values still use the separate money precision documented for portfolio accounting.

Universe liquidity ranking must use raw traded value, or raw close multiplied by raw volume when the exchange traded-value field is unavailable. It must not use adjusted price multiplied by adjusted volume.

## Required Messy Tests

The parser test set must include:

- a clean split;
- real NSE `Face Value Split (Sub-Division)` wording;
- a clean bonus;
- a date near a bonus ratio;
- a slash-separated non-ratio token;
- multiple ratio-shaped tokens;
- a combined split-plus-bonus string;
- a scheme-of-arrangement string containing bonus text;
- non-equity bonus instruments;
- ignored dividends / meetings / name changes;
- ignored buybacks;
- a consolidation;
- a rights issue;
- malformed split and bonus strings;
- validation refusing unsupported matching actions while allowing ignored no-ops.

## Real NSE Corpus Check

Before the adjusted data is trusted, run at least one year of actual NSE corporate-action purpose strings through the parser and report the distribution of parsed types versus quarantined records. Add any new failure modes discovered from the corpus before freezing the V0 universe.
