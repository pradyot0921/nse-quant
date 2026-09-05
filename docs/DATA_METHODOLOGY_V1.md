# Data Methodology V1 - Same-Date Corporate Actions

**Version:** `DATA_METHODOLOGY_V1_D078`
**Date:** 2026-09-05
**Scope:** Independent data infrastructure after Phase 2 closeout

## Boundary

This methodology adds an opt-in corporate-action API. It does not change the
legacy `parse_corporate_action()` API, the frozen V0 dataset builder, any
processed strategy dataset, the experiment ledger, or a strategy runner.
The term V1 here names this data methodology; the older corporate-action notes
used V1 for the original single-event parser. The version identifier above
disambiguates them.

B006 remains permanently CANCELLED and B006-S015 remains NOT_RUN. No C-series
experiment is created by this change. No strategy runs or validation-period
strategy inspection are permitted by it.

## Source And Components

`CorporateActionEvent` preserves the complete original `CorporateActionRecord`
alongside one or two `ParsedCorporateAction` components. Each component retains
the original symbol, purpose, ex-date, and record date. Components retain their
own action type, ratio, and price/volume factors.

`parse_corporate_action_event()` accepts a combined record only when the entire
normalized purpose matches exactly one equity bonus clause and one supported
face-value split clause, separated by a slash or the word `and`. Either clause
order is accepted; components have canonical BONUS then SPLIT order.

The bonus clause is `Bonus N:D`, with positive numbers and the existing
denominator ceiling of 20. Spaces around the colon are allowed. Split clauses
use an explicit old and new face value, with supported Face Value Split,
Stock split, or Sub-division wording, optional currency/per-share text, and a
strict decrease in positive face value. This is deliberately a narrow grammar;
it is not a general natural-language corporate-action parser.

Standalone `Bonus 1 : 1` is normalized only for parsing, retaining the original
source text. Existing single-event parsing is reused for other isolated forms.
Other slash-delimited or `and`-delimited multi-clause text is quarantined by
this API. Schemes, rights, mergers, demergers, consolidations, non-equity bonus
instruments, incomplete legs, multiple ratios, and unrecognized combined
wording remain unsupported. Rejection returns one UNSUPPORTED component for
the whole source, never a valid partial leg.

## Factor Composition

For an equity bonus of N new shares per D existing shares:

```text
bonus price factor = D / (D + N)
bonus volume factor = (D + N) / D
```

For a split from old face value F_old to F_new:

```text
split price factor = F_new / F_old
split volume factor = F_old / F_new
```

The supported combined event multiplies both component factors. It assumes
the bonus applies proportionally to the equity shares participating in the
split; wording requiring a different entitlement basis is outside the grammar.
TECHM's issuer evidence independently confirms this basis for the real fixture.

`event_components()` sorts by symbol, ex-date, action type, and purpose.
`adjust_ohlcv_events()` uses that order and the established backward-adjustment
and ISIN checks. Each factor is applied only to bars strictly before its
ex-date. Record date is retained for identifier continuity, not as a second
adjustment date.

Arithmetic uses local Decimal precision 28, existing per-component and
cumulative factor rounding to 10 decimal places with ROUND_HALF_UP, and the
existing six-decimal adjusted price and volume rounding. Per-step rounding is
preserved; mathematically equivalent rational expressions need not be bitwise
identical to independently rounded products. Canonical order makes this
methodology deterministic.

Duplicate or conflicting components keyed by `(symbol, ex_date, action_type)`
raise `DuplicateCorporateActionError`. This includes repeated combined rows,
a combined row plus a standalone copy of either leg, and two differing ratios
for the same type and date. The methodology does not silently deduplicate or
choose between revised records. A separate bonus row plus a separate split row
on the same date is permitted. Unknown components still halt adjustment through
the existing validation path.

## Real Data Validation

TECHM's 2014-15 annual report, PDF page 98 (printed page 97), describes a 1:1
bonus and a split from Rs 10 to Rs 5. It records conversion of the original
and bonus shares into two equal pools of split shares. This confirms four
shares per original share, so the combined historical price factor is 0.25
and the volume factor is 4.

Source: [Tech Mahindra annual report](https://cache.techmahindra.com/cache/investors/Annual-Report-FY14-15.pdf).

The NSE corporate-action row identifies 19 March 2015 as ex-date and 20 March
as record date. The validation uses only three NSE bhavcopies, 18-20 March
2015, plus that saved source row. Exact archives and source JSON are pinned
by SHA-256; the committed fixture preserves the selected facts.

See [TECHM data validation](validation/TECHM_2015_MULTI_ACTION_V1.md) and its
[machine-readable replay](validation/TECHM_2015_MULTI_ACTION_V1.json).

This is a local corporate-action continuity check, not a warm-up dataset build
or certification of all future corporate-action wording. A fresh strategy
input dataset still requires a separately frozen specification and its full
data audit.

## Next Research Boundary

After this upgrade is reviewed and merged, the proposed next step is a
separate **Research Cycle 2 / V1 Strategy Research** specification: at most two
baseline candidates, permanent results, unchanged numerical promotion gates,
and a cumulative record of every B001-B006 and C-series attempt, including
cancellations and conditional robustness rows.

That specification must define multiple-testing assessment and feasibility
before any promotion, including how Deflated Sharpe or SPA would be used and
what inputs and assumptions they require. No method is implemented or claimed
to have passed here. Event-specific diagnosis remains prohibited and
`2023-01-01 through 2026-08-19` remains sealed.

Only after the cycle specification may a new C001 preregistration adopt the
previously untested B006 signal unchanged. B006's cancellation cannot be
reversed. The data build and audit must precede C001 implementation review;
reuse of existing signal code must be reviewed under the new specification.
