# B006 Input Warm-Up Dataset V0

**Status:** Blocked before dataset build; B006 cancelled before research execution

**Date:** 2026-09-04

This artifact records the required B006 input-only warm-up data check. It is
not a B006 research result, does not run B006, does not run B006-S015, and does
not inspect validation-period strategy output.

## Scope

B006 requires adjusted OHLCV history before `2016-01-01` so that the first
eligible 2016 signal can compute the frozen PH52 score:

```text
PH52(i,T) =
adjusted_close(i,T)
/
max(adjusted_close(i,d) for ordinary sessions d where T - 364 calendar days <= d <= T)
```

For the first ordinary 2016 weekly signal date, the mechanically required
warm-up start is:

```text
2016-01-01 - 364 calendar days = 2015-01-02
```

Therefore the required B006 input-only warm-up window is:

```text
2015-01-02 through 2015-12-31
```

The research performance window remains unchanged:

```text
2016-01-01 through 2022-12-31
```

## Corporate-Action Audit

The 2015 NSE corporate-action scan completed successfully:

| Metric | Value |
| --- | ---: |
| Scan window | `2015-01-02` through `2015-12-31` |
| Endpoint rows | 1911 |
| EQ rows scanned | 1883 |
| Row-level failures | 0 |
| Split rows parsed | 30 |
| Bonus rows parsed | 26 |
| Ignored rows parsed | 1791 |
| Unsupported rows parsed | 36 |

Evidence:

```text
docs/validation/B006_CORPORATE_ACTION_WARMUP_SCAN_V0.md
```

## Selected-Universe Actions In 2015 Warm-Up Window

For the frozen `nifty100_v0_20_d037` universe, the 2015 scan found 33 selected
symbol corporate-action records.

Supported selected-symbol adjustment records:

| Symbol | Ex-Date | Type | Purpose | Price Factor |
| --- | --- | --- | --- | ---: |
| BANKBARODA | 2015-01-22 | SPLIT | Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 2/- Per Share | 0.2000000000 |
| INFY | 2015-06-15 | BONUS | Annual General Meeting/ Dividend - Rs 29.50/- Per Share And Bonus 1:1 | 0.5000000000 |
| KOTAKBANK | 2015-07-08 | BONUS | Bonus 1: 1 | 0.5000000000 |

Unsupported selected-symbol records:

| Symbol | Ex-Date | Purpose | Current parser status |
| --- | --- | --- | --- |
| HCLTECH | 2015-03-19 | Bonus 1 : 1 | Unsupported punctuation variant |
| TECHM | 2015-03-19 | Bonus 1:1 / Face Value Split - From Rs 10/- Per Share To Rs 5/- Per Share | Unsupported combined split-plus-bonus event |

The `HCLTECH` record is a narrow punctuation variant of an otherwise supported
bonus pattern. The `TECHM` record is the blocking item because D-016 states
that combined split-plus-bonus purpose strings are unsupported in V1 and must
remain quarantined until the parser can represent multiple actions on one
ex-date.

## Decision

Do not build `data/processed/nifty100_v0_52w_high_input_warmup.csv` under the
current corporate-action rules.

Do not run B006.

Do not run B006-S015.

Do not inspect validation.

B006 is cancelled before research execution because its required input-only
warm-up dataset cannot be built cleanly under the deterministic V0
corporate-action rules in force when B006 was pre-registered.

This is a data-validity stop, not evidence for or against the 52-week-high
ranking hypothesis.

The pre-registration called for this readiness decision before implementation.
Implementation was already merged under D-075 and PR #74 when the audit was
performed. D-076 records that sequencing discrepancy; cancellation here is
before dataset construction and research execution, but after implementation.

## What Would Be Required To Reopen This

Reopening a 52-week-high experiment would require a new pre-registered cycle,
not a B006 rescue trial.

At minimum, that later cycle would need:

- a new experiment ID;
- deterministic representation of same-date multi-action corporate events;
- tests for combined split-plus-bonus price and volume factors;
- a decision entry made before any new strategy result;
- a fresh input-dataset artifact; and
- the validation holdout still sealed until all research-period gates pass.

No such reopening is part of B006.
