# Phase 2 Interim Findings V0

**Status:** Interim finding before B006 selection

**Date:** 2026-09-04

This artifact records the Phase 2 research pattern after B004 and B005. It does
not pre-register B006, does not run B006, does not run any robustness row, and
does not inspect the validation holdout.

## Boundary

Allowed inputs used:

- committed B003, B004, and B005 research-period reports;
- committed B004 and B005 research-review artifacts;
- committed frozen research-period dataset and benchmark;
- deterministic reconstruction of the B003 research-period daily NAV series
  from the committed B003 rules, code, dataset, benchmark, universe, costs, and
  slippage settings.

Prohibited inputs not used:

- validation-period strategy NAV, trades, CAGR, Sharpe, drawdown, or other
  strategy-performance output;
- B004-S015 or B005-S015 robustness runs;
- B006 candidate results;
- parameter sweeps or alternative risk-overlay settings.

## Risk Overlay Finding

Two independent, externally motivated risk-management overlays were tested
after B003:

| Experiment | Mechanism | CAGR | Maximum drawdown | Sharpe | Completed round trips |
| --- | --- | ---: | ---: | ---: | ---: |
| B003 | No Phase 2 overlay | 0.136461 | 0.512654 | 0.636888 | 124 |
| B004 | Exogenous Nifty 100 TRI SMA200 regime filter | 0.071975 | 0.306676 | 0.446175 | 127 |
| B005 | Realized-volatility exposure scaling | 0.032527 | 0.302637 | 0.332169 | 253 |
| Nifty 100 TRI benchmark | Benchmark threshold | 0.137013 | 0.379228 | 0.837396 | N/A |

B004 and B005 both reduced maximum drawdown to roughly 30%, but both sacrificed
more than half of B003's CAGR and both lowered Sharpe. B005 also introduced a
previously unobserved mechanical cost: continuous exposure resizing doubled
completed round trips versus B003 while holding less exposure.

The durable finding is that Phase 2 risk overlays have not solved the binding
problem. In this V0 setting, reducing exposure improves drawdown but fails the
benchmark-matching return and risk-adjusted-performance gates. B006 should not
spend the final baseline slot on another risk-control overlay, a softer B004
filter, a different B005 volatility target or lookback, or a slippage rescue
trial.

## B003 Beta Diagnostic

No separate daily B003 NAV CSV is committed. For this diagnostic, the B003
daily NAV series was reconstructed from the committed deterministic B003
experiment path and then checked against the committed B003 report.

Reconstruction check:

| Metric | Reconstructed B003 | Committed B003 report |
| --- | ---: | ---: |
| Observations | 1726 | 1726 |
| Start date | 2016-01-01 | 2016-01-01 |
| End date | 2022-12-30 | 2022-12-30 |
| CAGR | 0.136461 | 0.136461 |
| Maximum drawdown | 0.512654 | 0.512654 |
| Sharpe | 0.636888 | 0.636888 |
| Completed round trips | 124 | 124 |

Daily simple-return regression of B003 strategy returns on Nifty 100 TRI
returns over the reconstructed research-period series:

| Metric | Value |
| --- | ---: |
| Daily return pairs | 1725 |
| Beta to Nifty 100 TRI | 1.016661 |
| Daily intercept | 0.000059 |
| Annualized arithmetic alpha | 0.014954 |
| Strategy annualized arithmetic mean return | 0.164253 |
| Benchmark annualized arithmetic mean return | 0.146852 |
| Beta-implied benchmark component | 0.149298 |
| Active annualized arithmetic mean return | 0.017401 |
| Correlation | 0.691312 |
| R-squared | 0.477912 |

The diagnostic does not support the hypothesis that B003 was simply a
concentrated 1.3-1.4 beta version of the index with near-zero alpha. B003 beta
was close to 1.0 and its regression alpha was modestly positive. The problem is
therefore not explained by hidden high beta alone.

The better interpretation is narrower: B003 may contain some return signal, but
not enough to clear the project gates once implemented as a concentrated
three-position delivery-cost strategy with large drawdowns. This keeps B006
directionally pointed at return generation, but it does not justify tuning B003
parameters.

## Implication For B006

B006 is the final unused Phase 2 baseline slot. It should be selected only if a
genuinely different, externally motivated return-side mechanism can be written
before implementation.

B006 may target:

- a materially different stock-selection signal;
- a materially different ranking input;
- a universe-breadth question that is explicitly scoped and feasible under the
  existing data/governance constraints.

B006 may not be:

- another risk overlay;
- a different B004 SMA length, threshold, or cadence;
- a different B005 volatility target, lookback, or exposure cap;
- a B003 momentum lookback, entry-rank, hold-rank, position-count, or cadence
  tweak;
- a slippage or cost rescue trial.

If no externally motivated return-side mechanism is strong enough to
pre-register, the correct next step is to stop Phase 2 and write up the V0
finding rather than spend the final baseline slot because it remains available.

## Next Rule

Before B006 implementation or execution, the repository must contain a merged
`docs/validation/B006_PREREGISTRATION_V0.md` that states the mechanism,
external basis, fixed parameters, gates, expected failure modes, and validation
holdout boundary.

The validation holdout remains sealed:

```text
2023-01-01 through 2026-08-19
```
