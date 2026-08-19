# Corporate-Action Adjustment Notes

**Status:** Phase 1 implementation note  
**Decision anchor:** D-016 in `docs/DECISIONS.md`

## V1 Supported Actions

The first corporate-action parser supports only deterministic single-event actions:

- stock splits where the purpose text contains an old face value and a new face value;
- bonus issues where the purpose text contains exactly one colon-separated ratio.

All other events are unsupported in V1 and must be quarantined for manual review before downstream data is trusted.

## Ambiguous Or Combined Events

A single NSE purpose string that contains both a split and a bonus is unsupported in V1.

The current parser returns one `ParsedCorporateAction`, so it cannot safely represent two actions on the same ex-date. Until the model supports multiple parsed events from one source record, combined split-plus-bonus text must quarantine instead of silently dropping one action.

Unsupported or ambiguous events affecting a frozen-universe symbol during the research window must halt or quarantine dataset construction. Logging and continuing with an unadjusted series is not acceptable.

## Bonus Ratio Parsing

Bonus ratios use a colon separator. Slash-separated tokens are not accepted as bonus ratios because they collide with dates in NSE purpose text.

If more than one colon-shaped ratio token appears in the purpose text, the record is unsupported. The parser must not pick the first ratio and continue.

## Adjustment Precision

Corporate-action factors are `Decimal` values quantized to 10 decimal places using `ROUND_HALF_UP`.

Adjusted OHLC prices are quantized to `Decimal("0.000001")` rupees after applying cumulative factors. Adjusted volume is adjusted alongside price and quantized to six decimal places.

Final accounting and NAV values still use the separate money precision documented for portfolio accounting.

## Required Messy Tests

The parser test set must include:

- a clean split;
- a clean bonus;
- a date near a bonus ratio;
- a slash-separated non-ratio token;
- multiple ratio-shaped tokens;
- a combined split-plus-bonus string;
- a consolidation;
- a rights issue;
- malformed split and bonus strings.

## Real NSE Corpus Check

Before the adjusted data is trusted, run at least one year of actual NSE corporate-action purpose strings through the parser and report the distribution of parsed types versus quarantined records. Add any new failure modes discovered from the corpus before freezing the V0 universe.
