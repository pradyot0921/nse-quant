# Phase 2 Hypothesis Intake Template

**Status:** Template only

**Created:** 2026-09-03

This document is the required starting point for any new post-Phase 1 research
cycle. It is not a strategy proposal, not an experiment result, and not
permission to inspect the validation holdout.

Copy this template into a new pre-registration artifact before running any new
strategy, risk overlay, universe change, rebalance rule, cost assumption, or
parameter choice.

## Required File Name

Use a new experiment ID in the filename:

```text
docs/validation/<EXPERIMENT_ID>_PREREGISTRATION_V0.md
```

Example shape only:

```text
docs/validation/C001_PREREGISTRATION_V0.md
```

Do not reuse B001, B002, B003, B001-S015, B002-S015, or B003-S015.

## Experiment Identity

| Field | Value |
| --- | --- |
| Experiment ID | TBD |
| Short name | TBD |
| Author | TBD |
| Pre-registration date | TBD |
| Research period | 2016-01-01 through 2022-12-31 unless explicitly changed before testing |
| Validation holdout | 2023-01-01 through 2026-08-19, sealed |
| Prior related experiments | B001, B002, B003 |

## Hypothesis

State the hypothesis before running the experiment.

```text
TBD
```

## Economic Reasoning

Explain why the expected return source should exist.

This section must be about the market mechanism, investor behavior, structural
constraint, risk transfer, or implementation edge being tested. It must not be
just a claim that a parameter value may perform better.

```text
TBD
```

## Difference From Rejected Phase 1 Candidates

Explain why this is genuinely different from the rejected V0 concentrated
large-cap momentum family.

The explanation must address why this is not merely:

- a lookback tweak;
- a position-count tweak;
- a rebalance-frequency tweak;
- a slippage/cost assumption tweak;
- a post-hoc rescue of B001, B002, B003, B001-S015, B002-S015, or B003-S015.

```text
TBD
```

## Universe And Data

| Field | Value |
| --- | --- |
| Universe rule | TBD |
| Universe version | TBD |
| Dataset version | TBD |
| Benchmark | TBD |
| Corporate-action treatment | TBD |
| Exclusions | TBD |

If the universe changes, freeze the new selection rule before running the
experiment.

## Strategy Rules

Define exact rules before execution.

| Rule Area | Pre-Registered Rule |
| --- | --- |
| Signal inputs | TBD |
| Entry rule | TBD |
| Exit rule | TBD |
| Ranking rule | TBD |
| Position sizing | TBD |
| Rebalance schedule | TBD |
| Cash handling | TBD |
| Missing-data handling | TBD |
| Corporate-action handling | TBD |

## Execution And Costs

| Field | Value |
| --- | --- |
| Execution timing | TBD |
| Fill-price rule | TBD |
| Slippage assumption | TBD |
| Cost profile | TBD |
| Turnover measurement | TBD |
| Unfilled-order policy | TBD |

Any changed cost or slippage assumption needs independent justification before
results are known.

## Promotion Gates

Define the exact research-period gates before execution.

| Gate | Threshold | Reason |
| --- | --- | --- |
| CAGR or return gate | TBD | TBD |
| Drawdown gate | TBD | TBD |
| Benchmark-relative gate | TBD | TBD |
| Turnover gate | TBD | TBD |
| Minimum trade count | TBD | TBD |
| Any additional risk gate | TBD | TBD |

The validation holdout may only be inspected after the candidate passes every
pre-registered research-period gate.

## Expected Failure Modes

List what would make the hypothesis fail or become economically unconvincing.

```text
TBD
```

## Stop Rules

The experiment must stop in research if any pre-registered gate fails.

Do not inspect validation-period strategy performance to rescue, tune, rank, or
reinterpret a failed research-period candidate.

## Output Artifacts

List the artifacts expected from the run.

| Artifact | Path |
| --- | --- |
| Pre-registration | TBD |
| Ledger row | TBD |
| Research result directory | TBD |
| Research report | TBD |
| Review or closeout note | TBD |

## Approval To Run

Before execution, confirm:

- [ ] The experiment has a new ID.
- [ ] The hypothesis is written before testing.
- [ ] The economic reasoning is written before testing.
- [ ] The difference from B001/B002/B003 is explicit.
- [ ] The universe and data version are frozen or named.
- [ ] The research-period gates are written before testing.
- [ ] The validation holdout remains sealed.
- [ ] The experiment is not a rescue trial.

No run should start until every box above is complete.
