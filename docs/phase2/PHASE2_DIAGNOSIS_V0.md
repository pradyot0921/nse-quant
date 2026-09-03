# Phase 2 Diagnosis V0

**Status:** Stage 2.1 diagnosis complete

**Diagnosis date:** 2026-09-03

**Stage deadline:** 2026-09-05 23:59 Asia/Kolkata

This document is the Stage 2.1 diagnosis required by
`docs/PHASE_2_RESEARCH_SPEC.md`.

It does not run B004, does not simulate a market-regime filter, does not inspect
regime switch dates, does not identify in-sample loss episodes, and does not
inspect the validation holdout.

## Boundary

Allowed inputs used:

- already-published Phase 1 aggregate results and closeout artifacts;
- the locked Phase 2 specification;
- external literature on trend following and momentum crash risk;
- implementation-level reasoning that does not generate a strategy result.

Prohibited inputs not used:

- worst B001/B002/B003 dates, weeks, months, or episodes;
- stock-level attribution of Phase 1 losses;
- candidate filter switch dates;
- alternative moving-average lengths or thresholds;
- counterfactual drawdown-avoidance tests;
- validation-period strategy output.

## Diagnosis

The B004 premise is coherent enough to implement under the locked specification.

Phase 1 showed a useful but incomplete fact pattern: the rejected momentum
family could produce positive trade-level statistics while failing
portfolio-level risk gates. B001 had positive expectancy and profit factor, but
the concentrated weekly portfolio still breached drawdown and turnover
discipline. B003 reduced turnover through hysteresis, but still failed the
benchmark-relative drawdown gate.

The general diagnosis is therefore not that every relative-momentum trade is
economically empty. The diagnosis is that the frozen V0 implementation exposed
too much capital to concentrated equity downside while relying on a small number
of held names. A valid Phase 2 question is whether an externally specified
broad-market trend filter can reduce that downside exposure without becoming an
in-sample repair.

## External Mechanism

The 200-session trend concept in B004 is externally motivated before the run.
Faber's tactical asset allocation work presents a simple long-term moving
average timing model intended to improve risk-adjusted asset-allocation results
across markets. The Phase 2 specification does not claim to replicate Faber's
portfolio. It adapts the externally documented long-term trend idea to the
project's Nifty 100 TRI benchmark and weekly decision cadence.

Daniel and Moskowitz document a separate but relevant mechanism: momentum
strategies can suffer severe negative episodes, especially around stressed
market states and rebounds. That supports studying market-regime risk as a
general phenomenon. It does not justify designing a rule around any particular
2016-2022 loss episode.

## Why B004 Is Not A Rescue Trial

B004 is not a rescue trial because its material parameters were frozen before
Stage 2.1 diagnosis:

- 200 ordinary-session Nifty 100 TRI SMA;
- `RISK_ON` only when TRI is greater than SMA200;
- `RISK_OFF` when TRI is less than or equal to SMA200;
- weekly evaluation only;
- no intraweek regime exit;
- unchanged B003 stock lookback, entry rank, hold rank, and position count;
- unchanged baseline slippage.

No alternative SMA length, threshold, cadence, position count, or lookback is
eligible to replace B004 after seeing results.

## Implementation Risks To Test

The main B004 risks are implementation and interpretation risks, not parameter
selection questions.

First, the SMA200 calculation must be strictly point-in-time. The signal date
may use the current and prior 199 ordinary benchmark observations, but it must
not backfill warm-up observations or use future benchmark levels.

Second, the weekly cadence must remain exact. The regime state is evaluated only
at the normal weekly decision point. A daily benchmark move must not trigger an
intraweek exit.

Third, the `RISK_OFF` behavior must preserve accounting truth. It may schedule
full exits and block new entries, but it cannot fabricate fills. Unfilled exits
must remain held and be retried under the existing execution rules.

Fourth, the report must separate exposure reduction from evidence of edge. A
lower drawdown alone is not enough. B004 must also pass the frozen CAGR, Sharpe,
turnover, integrity, and concentration gates.

Fifth, the regime-sample limitation must be visible in every B004 report. The
research window contains few broad-market regime episodes, so any observed
benefit is not precise evidence that the filter parameter has been estimated.

## Fatal-Problem Check

No fatal conceptual issue was found that requires cancelling B004 before
implementation.

B004 remains:

```text
PLANNED
```

This does not imply likely success. It means the frozen hypothesis has enough
external basis and internal clarity to proceed to Stage 2.2 implementation and
Stage 2.3 synthetic/unit validation.

## Stage 2.2 Requirements

Implementation may now proceed only within the locked B004 rule:

- calculate a 200-session SMA on Nifty 100 TRI ordinary research sessions;
- produce weekly regime states without look-ahead;
- treat warm-up as cash/no-entry;
- schedule full exits and prohibit entries when weekly state is `RISK_OFF`;
- delegate to B003 ranking and hysteresis when weekly state is `RISK_ON`;
- preserve existing execution, sizing, cost, and unfilled-order behavior;
- add regime exposure and transition reporting;
- add stock and calendar-year return-concentration reporting;
- block validation-period strategy execution without a later Phase 3 artifact.

## Sources

- Mebane T. Faber, *A Quantitative Approach to Tactical Asset Allocation*, The
  Journal of Wealth Management, Spring 2007; SSRN
  <https://ssrn.com/abstract=962461>.
- Meb Faber Research, Episode #86 discussion of the 200-day SMA / 10-month SMA
  trend-following framing,
  <https://mebfaber.com/2017/12/13/episode-86-quantitative-approach-tactical-asset-allocation/>.
- Kent Daniel and Tobias J. Moskowitz, *Momentum Crashes*, Journal of Financial
  Economics 122(2), 2016, pp. 221-247,
  <https://doi.org/10.1016/j.jfineco.2015.12.002>.

## Close

Stage 2.1 is complete. The next valid repository stage is Stage 2.2
implementation of the frozen B004 rule, followed by Stage 2.3 synthetic/unit
validation.

B004 must still not be run on the real research period until implementation and
synthetic/unit validation are complete.

The validation holdout remains sealed:

```text
2023-01-01 through 2026-08-19
```
