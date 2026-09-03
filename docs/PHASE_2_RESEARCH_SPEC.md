# Phase 2 — New Strategy Research Specification

**Project:** NSE Quant Research and Trading System  
**Phase:** 2  
**Status:** PRE-REGISTERED — NO PHASE 2 STRATEGY RUN YET  
**Specification date:** 3 September 2026  
**Primary objective:** Develop a genuinely new, externally motivated research candidate that addresses the downside-risk weakness exposed in Phase 1 without spending the validation holdout.  
**Research period:** `2016-01-01..2022-12-31`  
**Validation holdout:** `2023-01-01..2026-08-19` — **SEALED**  
**Frozen Phase 1 universe:** `nifty100_v0_20_d037`  
**Frozen Phase 1 dataset:** `nifty100_v0_adjusted_ohlcv_d039`  
**Benchmark:** Nifty 100 TRI  

---

## 1. Phase 2 Purpose

Phase 1 proved the research and accounting pipeline and then rejected all three baseline strategy candidates before validation:

| Experiment | Research outcome |
| --- | --- |
| `B001` | REJECTED — turnover FAIL, drawdown FAIL |
| `B002` | REJECTED — turnover FAIL, drawdown FAIL |
| `B003` | REJECTED — turnover PASS, drawdown FAIL |

Phase 2 is therefore **not** a continuation of B001/B002/B003 tuning.

Phase 2 asks a new question:

> Can an externally motivated market-regime risk overlay reduce the downside weakness of the existing relative-momentum/hysteresis structure while retaining acceptable return, risk-adjusted performance, turnover, and diversification?

The immediate Phase 2 candidate is `B004`.

Phase 2 must not inspect strategy performance on the validation holdout.

---

## 2. Research-Integrity Boundary

### 2.1 Holdout remains sealed

The validation period remains:

```text
2023-01-01 through 2026-08-19
```

No Phase 2 strategy may be run on this period until a separate Phase 3 promotion decision is recorded.

In particular, Phase 2 must not:

- run `B001`, `B002`, or `B003` on validation;
- run `B001-S015`, `B002-S015`, or `B003-S015` as rescue trials;
- run `B004` or any later Phase 2 candidate on validation;
- inspect validation-period strategy NAV, trades, Sharpe, CAGR, drawdown, or any other strategy-performance output;
- use validation-period performance to choose any Phase 2 rule or parameter.

Data-integrity maintenance that is independent of strategy performance does not spend the holdout, but any strategy-derived inspection does.

### 2.2 Phase 1 failures stay failed

Phase 1 results are permanent.

A Phase 2 candidate receives a new experiment ID. It must never overwrite, rename, reclassify, or retroactively modify `B001`, `B002`, or `B003`.

---

## 3. Anti-Overfitting Rule for Diagnosis

### 3.1 Diagnosis is general-phenomenon diagnosis only

Phase 2 diagnosis must stay at the level of externally documented mechanisms and already-published Phase 1 aggregate results.

Allowed inputs:

- the final aggregate Phase 1 reports;
- the Phase 1 research review and closeout artifacts;
- published research on momentum crashes, trend following, market-regime risk, concentration, and related general mechanisms;
- code/accounting review that does not create a new strategy result.

The diagnosis may state general claims such as:

> Momentum strategies can experience severe losses around panic/rebound states.

It may **not** state or investigate claims such as:

> The strategy lost in a specific month, therefore a rule should be designed to avoid that month.

### 3.2 Prohibited diagnosis activities

Before `B004` is run, Stage 2.1 must not:

- identify or rank the worst B001/B002/B003 dates, weeks, months, or episodes;
- create event-specific drawdown narratives;
- inspect which individual stocks caused the worst Phase 1 losses;
- inspect the exact historical dates on which a proposed regime filter would have switched state;
- simulate a candidate risk filter;
- test alternative moving-average lengths;
- test alternative regime thresholds;
- run counterfactual "what would have avoided this drawdown?" analyses;
- perform parameter sweeps, grids, optimization, or search;
- inspect the validation holdout.

This rule exists because designing a rule to remove the exact observed 2016–2022 losses would be in-sample fitting even if the 2023–2026 holdout remained untouched.

### 3.3 Diagnosis deliverable and deadline

Stage 2.1 has one deliverable:

```text
docs/phase2/PHASE2_DIAGNOSIS_V0.md
```

The diagnosis must be completed no later than:

```text
5 September 2026, 23:59 Asia/Kolkata
```

It is limited to one primary diagnosis document.

After that deadline, Stage 2.1 closes. Any later material change to the diagnosis must be recorded as a new decision rather than silently editing the original rationale.

### 3.4 B004 is frozen before diagnosis

`B004` is specified in this document **before** Stage 2.1 diagnosis begins.

The diagnosis therefore cannot choose B004's moving-average length, signal threshold, cadence, or portfolio rule.

If the diagnosis discovers a fatal conceptual or implementation problem with B004, the candidate may be marked:

```text
CANCELLED_BEFORE_RUN
```

with a written reason.

It may not be silently repaired. A replacement requires a new experiment ID.

---

## 4. External Basis for B004

### 4.1 Exogenous trend rule

The market-regime rule is sourced externally rather than selected from 2016–2022 performance.

Mebane Faber's *A Quantitative Approach to Tactical Asset Allocation* discusses the 200-day simple moving average as a standard long-term trend measure and implements the monthly 10-month moving-average analogue in the published timing model.

Phase 2 adapts that **externally specified 200-day concept** to the daily Nifty 100 TRI series.

This is not claimed to be an exact replication of Faber's published portfolio. The adaptation is:

- Indian benchmark: Nifty 100 TRI;
- daily observations;
- 200 ordinary NSE research sessions;
- evaluation at the project's existing weekly decision point;
- use as a risk overlay on the frozen relative-momentum/hysteresis strategy.

No alternative SMA length will be tested for B004.

### 4.2 General momentum-risk motivation

External momentum literature documents that momentum strategies can suffer infrequent severe losses, especially around panic/rebound states.

This general external phenomenon is a permitted motivation for studying a market-regime risk overlay.

The B004 rule is not justified by identifying which specific Phase 1 dates it would have avoided.

### 4.3 References

1. Mebane T. Faber, *A Quantitative Approach to Tactical Asset Allocation*, The Journal of Wealth Management, Spring 2007; updated version available via SSRN: <https://ssrn.com/abstract=962461>.
2. Meb Faber Research, discussion of the long-term 200-day SMA / 10-month SMA timing rule: <https://mebfaber.com/2017/12/13/episode-86-quantitative-approach-tactical-asset-allocation/>.
3. Kent Daniel and Tobias J. Moskowitz, *Momentum Crashes*, Journal of Financial Economics 122(2), 2016, pp. 221–247, DOI: <https://doi.org/10.1016/j.jfineco.2015.12.002>.

**Repository-history note:** the current frozen `docs/PHASE_0_PROJECT_SPEC.md` does not contain a Faber citation. Phase 2 introduces this source explicitly here rather than rewriting Phase 0 history.

---

## 5. Phase 2 Trial Budget

Phase 2 has a hard cap of:

```text
MAXIMUM BASELINE PHASE 2 CANDIDATES: 3
```

The reserved baseline IDs are:

```text
B004
B005
B006
```

`B004` consumes the first slot.

The cap cannot be increased after seeing a Phase 2 result.

### 5.1 What counts as a baseline candidate

Any materially different hypothesis counts as a baseline candidate.

Examples:

- a new market-regime mechanism;
- a new stock-selection mechanism;
- a new portfolio-construction mechanism;
- a new risk overlay;
- a materially different universe rule.

### 5.2 Parameter variants are not free trials

Changing any of the following creates a separate trial and cannot be hidden inside one experiment:

- momentum lookback;
- SMA length;
- regime threshold;
- rebalance cadence;
- entry rank;
- hold rank;
- position count;
- stop rule;
- slippage assumption;
- universe.

Phase 2 specifically prohibits testing SMA-100, SMA-150, SMA-250, or similar alternatives merely to see whether they improve the B004 result.

### 5.3 Robustness variants

A robustness variant may run only after its baseline candidate passes every baseline promotion gate.

A robustness run:

- is separately logged;
- cannot rescue a failed baseline;
- does not authorize parameter selection;
- does not reopen the validation holdout.

For B004 the only currently pre-registered robustness variant is `B004-S015`.

---

## 6. B004 — Pre-Registered Strategy Specification

### 6.1 Experiment identity

```text
Experiment ID: B004
Name: Weekly relative momentum with hysteresis + exogenous market-trend filter
Direction: long/cash
Starting capital: ₹50,000
Research period: 2016-01-01..2022-12-31
Validation: SEALED
Universe: nifty100_v0_20_d037
Dataset: nifty100_v0_adjusted_ohlcv_d039
Benchmark: Nifty 100 TRI
Cost profile: ZERODHA_NSE_DELIVERY_2026_08
Baseline slippage: adverse deterministic 0.05%
```

### 6.2 Stock ranking

Unchanged from B003:

```text
Lookback: 60 ordinary trading sessions
Ranking: relative momentum across the frozen 20-stock universe
Rebalance decision: after close of final ordinary NSE research session of week
Entry: rank <= 3
Hold: rank <= 6
Exit: rank > 6 or ineligible
Maximum positions: 3
Execution: next eligible NSE session open
```

No momentum parameter is changed in B004.

### 6.3 Market-regime filter

Input:

```text
Nifty 100 TRI
ordinary NSE research sessions only
```

Trend measure:

```text
SMA200(T) = arithmetic mean of Nifty 100 TRI levels
            for T and the preceding 199 ordinary research sessions
```

Regime rule after weekly close on signal date `T`:

```text
RISK_ON  if TRI(T) > SMA200(T)
RISK_OFF if TRI(T) <= SMA200(T)
```

Equality is deliberately classified as `RISK_OFF`.

The filter is evaluated **only at the normal weekly strategy decision point**.

There is no intraweek regime exit in B004.

### 6.4 Warm-up

Before 200 Nifty 100 TRI ordinary-session observations exist:

```text
market regime = NOT_AVAILABLE
portfolio target = cash
new entries = prohibited
```

The strategy must not backfill or use future observations to create the SMA200 warm-up.

### 6.5 Risk-on behaviour

When the weekly regime is `RISK_ON`:

- use the B003 entry/hold/exit ranking rules;
- schedule resulting orders for the next eligible session open;
- execute exits before entries;
- retain all existing Phase 1 cash, sizing, cost, and unfilled-order rules.

### 6.6 Risk-off behaviour

When the weekly regime is `RISK_OFF`:

- schedule full exits for every held position at the next eligible session open;
- do not create new entries;
- remain in cash until a later weekly signal date is `RISK_ON`.

If an exit cannot execute:

```text
EXIT_UNFILLED
CARRY_POSITION_FORWARD
RETRY NEXT ELIGIBLE SESSION
```

The regime filter never fabricates a fill.

### 6.7 No rule search

The following are frozen before the first B004 run:

```text
200-session SMA length
TRI > SMA risk-on rule
TRI <= SMA risk-off rule
weekly evaluation only
60-session stock momentum
entry rank <= 3
hold rank <= 6
maximum 3 positions
0.05% baseline slippage
```

No alternative version may be previewed and substituted into B004.

---

## 7. B004-S015 — Pre-Registered Robustness Variant

```text
Experiment ID: B004-S015
Same rules as B004
Only change: adverse deterministic slippage = 0.15%
```

Run `B004-S015` **only if B004 passes every baseline promotion gate**.

It is not a rescue trial.

For robustness to pass, `B004-S015` must independently pass the same promotion gates defined below.

---

## 8. Exact Research-Period Promotion Gates

The gates are frozen before B004 runs.

The Phase 1 benchmark statistics over the identical research period are already known and are therefore fixed as Phase 2 thresholds under the existing metric definitions.

### 8.1 Integrity gate

```text
Accounting/state-integrity violations: 0
Unexplained NAV differences: 0
Unsupported held-security corporate-action breaches: 0
```

Any integrity failure rejects the run regardless of performance.

### 8.2 Turnover gate

For every complete calendar year:

```text
completed round trips <= 30
```

Any complete year above 30 rejects the candidate.

Partial edge years are reported but excluded from PASS/FAIL.

### 8.3 Maximum-drawdown gate

Research-period Nifty 100 TRI maximum drawdown:

```text
0.379228
= 37.9228%
```

Required:

```text
strategy maximum drawdown <= 0.379228
```

### 8.4 Minimum CAGR gate

Research-period Nifty 100 TRI CAGR:

```text
0.137013
= 13.7013%
```

Required:

```text
strategy CAGR >= 0.137013
```

### 8.5 Minimum Sharpe gate

Under the Phase 1 metric convention:

```text
benchmark Sharpe = 0.837396
```

Required:

```text
strategy Sharpe >= 0.837396
```

Metric convention:

```text
daily strategy NAV returns
252 trading sessions/year
risk-free rate = 0
```

### 8.6 Return-concentration gate — single stock

Define, for each symbol:

```text
symbol_positive_pnl =
max(total net realized completed-trade P&L for that symbol, 0)

stock_positive_contribution_share =
symbol_positive_pnl /
sum(symbol_positive_pnl across all symbols)
```

Required:

```text
maximum stock_positive_contribution_share <= 0.30
```

Therefore no one stock may provide more than **30% of total positive realized trade P&L**.

If total positive realized trade P&L is zero, the candidate fails the return gate before this concentration statistic is relevant.

### 8.7 Return-concentration gate — single calendar year

For each complete research calendar year define:

```text
year_positive_nav_gain =
max(year-end NAV - prior year-end NAV, 0)

year_positive_contribution_share =
year_positive_nav_gain /
sum(year_positive_nav_gain across complete years)
```

For 2016, use the frozen starting NAV as the prior boundary.

Required:

```text
maximum year_positive_contribution_share <= 0.35
```

Therefore no one complete calendar year may provide more than **35% of total positive annual NAV gains**.

This is the project's explicit concentration proxy. It is used instead of subjective statements such as "the result does not depend too much on one year."

### 8.8 Required reporting metrics

The following must be reported even where they are not separate promotion gates:

- net return;
- gross P&L before transaction costs, with slippage treatment explicitly labelled;
- transaction costs;
- CAGR;
- annualized volatility;
- maximum drawdown;
- Sharpe;
- Sortino;
- Calmar;
- completed round trips;
- annual turnover gate detail;
- time invested;
- average holding period;
- win rate;
- profit factor;
- average winner;
- average loser;
- expectancy;
- number of market-regime state changes;
- percentage of research sessions classified risk-on/risk-off once the SMA200 is available;
- stock contribution concentration;
- calendar-year contribution concentration;
- direct B004-versus-B003 comparison using the same research period, universe, dataset, benchmark, cost profile, and baseline slippage, including at minimum CAGR, maximum drawdown, Sharpe, turnover, transaction costs, and time invested.

### 8.9 Promotion rule

B004 is eligible for the robustness stage only if **every** gate above passes.

There is no discretionary override.

A high CAGR cannot compensate for a drawdown, turnover, Sharpe, integrity, or concentration failure.

---

## 9. Regime-Sample Limitation

The 2016–2022 research period contains only a small number of economically meaningful broad-market regime episodes.

B004 does **not** estimate the 200-session parameter from those episodes; the rule is externally specified before the run.

Nevertheless, evaluation of the regime overlay remains episode-sensitive.

Therefore every B004 report must state:

```text
REGIME-SAMPLE LIMITATION:
THE RESEARCH WINDOW CONTAINS FEW INDEPENDENT BROAD-MARKET REGIME EPISODES.
THE SMA200 RULE IS EXOGENOUSLY SPECIFIED, BUT ITS OBSERVED PERFORMANCE IN THIS
WINDOW HAS WIDE EPISODE-LEVEL UNCERTAINTY.
DO NOT INTERPRET A GOOD RESULT AS PRECISE ESTIMATION OF REGIME PERFORMANCE.
```

The project must report the realized number of filter state transitions after the run, but it must not change the rule because that number looks too small or too large.

---

## 10. Stage Sequence

### Stage 2.0 — Lock Phase 2 specification

Deliverable:

```text
docs/PHASE_2_RESEARCH_SPEC.md
```

Requirements:

- merge this specification before any B004 code or run;
- add B004 and B004-S015 to the experiment ledger as `PLANNED`;
- record the Phase 2 trial cap;
- record exact promotion thresholds;
- keep validation sealed.

### Stage 2.1 — General diagnosis

Deliverable:

```text
docs/phase2/PHASE2_DIAGNOSIS_V0.md
```

Deadline:

```text
5 September 2026, 23:59 Asia/Kolkata
```

No strategy run is allowed in this stage.

### Stage 2.2 — B004 implementation

Implement only what is needed for the frozen B004 rule:

- 200-session Nifty 100 TRI SMA calculation;
- weekly regime state;
- risk-off full-exit/no-entry behavior;
- warm-up behavior;
- report fields for regime exposure/transitions;
- concentration metrics;
- hard validation-period execution guard.

No alternative SMA lengths or regime rules.

### Stage 2.3 — Synthetic/unit validation

Before the real B004 research run, test at minimum:

1. exactly 199 benchmark observations => regime unavailable;
2. exactly 200 observations => deterministic SMA available;
3. `TRI > SMA200` => risk-on;
4. `TRI == SMA200` => risk-off;
5. `TRI < SMA200` => risk-off;
6. risk-off schedules full exits;
7. risk-off creates no entries;
8. unfilled risk-off exit is carried and retried;
9. risk-on delegates to frozen B003 ranking/hysteresis;
10. weekly-only evaluation — no intraweek filter action;
11. no look-ahead in SMA calculation;
12. ordinary-session-only SMA input;
13. missing required benchmark observation fails loudly;
14. concentration metrics reproduce hand-calculated fixtures;
15. validation-period runner is blocked without a Phase 3 promotion artifact.

### Stage 2.4 — B004 research run

Run:

```text
B004
2016-01-01..2022-12-31 only
```

Permanently record the result in the ledger.

No validation.

### Stage 2.5 — Gate review

Apply every frozen promotion gate.

If any gate fails:

```text
B004 = REJECTED
B004-S015 = NOT RUN
```

Do not rescue B004 by changing the SMA, threshold, cadence, or other parameter.

### Stage 2.6 — Robustness

Only if B004 passes every baseline gate:

```text
run B004-S015
research period only
```

`B004-S015` must pass the same gates.

If it fails:

```text
B004 baseline result remains recorded
Phase 3 promotion = NO
```

### Stage 2.7 — Phase 2 promotion review

If B004 and B004-S015 both pass:

- write a Phase 2 promotion-review artifact;
- mark B004 `CANDIDATE` or equivalent approved research status;
- stop;
- do not automatically run validation.

Validation belongs to Phase 3.

---

## 11. B005/B006 Governance

If B004 fails, Phase 2 may use at most the remaining two baseline slots:

```text
B005
B006
```

Before either is implemented:

- write a separate pre-registration;
- identify an externally motivated economic mechanism;
- freeze every material parameter;
- prove it is not merely a B004 parameter variant;
- count it against the three-candidate cap.

B005/B006 may not be:

```text
B004 with SMA150
B004 with SMA180
B004 with SMA250
B004 with a slightly different crossover threshold
B004 with a cadence selected after seeing B004
```

After three baseline candidates have run or been cancelled after implementation began, Phase 2 stops.

The cap cannot be extended because "one more test" looks promising.

---

## 12. Multiple-Testing Record

Phase 0 already requires permanent experiment logging and anticipates multiple-testing-aware methods including Deflated Sharpe Ratio, White's Reality Check, Hansen's SPA, walk-forward analysis, purged validation, and combinatorial purged cross-validation where appropriate.

Phase 2 must maintain a trial registry containing every:

- baseline candidate;
- robustness variant;
- cancelled-after-implementation experiment;
- parameter change that reached execution;
- failed result.

If the Phase 2 trial set expands beyond B004/B005/B006 plus their explicitly pre-registered robustness checks, Phase 2 is out of specification and must stop.

No winner may be presented without the full trial count.

---

## 13. Phase 2 Exit Criteria

Phase 2 ends in one of two valid states.

### Outcome A — candidate ready for Phase 3

Required:

```text
B004/B005/B006 baseline passes all frozen gates
AND
its pre-registered robustness check passes all required robustness gates
AND
all artifacts/tests are complete
AND
validation remains uninspected
```

Status:

```text
PHASE 2 COMPLETE
ONE CANDIDATE ELIGIBLE FOR PHASE 3 ONE-TIME VALIDATION
```

### Outcome B — no candidate

If all allowed Phase 2 baseline slots are rejected or cancelled:

```text
PHASE 2 COMPLETE
NO CANDIDATE PROMOTED
VALIDATION HOLDOUT REMAINS SEALED
```

This is a legitimate research result.

Failure to find a candidate does not authorize expanding the trial cap.

---

## 14. Phase 3 Boundary

Phase 3 is reserved for **one-time validation** of a candidate that has already passed Phase 2 research and robustness requirements.

Phase 2 must never consume:

```text
2023-01-01..2026-08-19
```

for strategy evaluation.

A separate Phase 3 specification must define:

- exactly which candidate is entering validation;
- the frozen code/data/parameter commit hashes;
- validation metrics and pass/fail rules;
- one-time inspection procedure;
- what happens after pass or fail;
- prohibition on retuning and reusing the same holdout.

---

## 15. Phase 2 Stop Rules

Stop immediately and record the event if any of the following occurs:

- validation-period strategy output is accidentally inspected;
- a hidden parameter sweep is discovered;
- a B004 parameter is changed after seeing B004 results without a new experiment ID;
- the baseline-candidate cap is exceeded;
- experiment results are deleted or overwritten;
- accounting/state-integrity checks fail;
- a candidate is run with rules that differ from its pre-registration.

A contaminated holdout or unlogged parameter search is a research-governance failure, not a minor documentation issue.

---

## 16. Immediate Next Action

Do **not** run B004 yet.

The next repository actions are:

```text
1. Commit and merge this Phase 2 specification.
2. Add B004 and B004-S015 as PLANNED ledger rows.
3. Record the three-baseline-candidate Phase 2 cap.
4. Produce PHASE2_DIAGNOSIS_V0.md under the Stage 2.1 restrictions.
5. Close Stage 2.1 by 5 September 2026, 23:59 Asia/Kolkata.
6. Implement exactly the frozen B004 rule.
7. Run tests.
8. Stop for review before the first real B004 research run.
```

No strategy performance is generated before Steps 1–7 are complete.
