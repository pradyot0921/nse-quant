# B006 Pre-Registration V0

**Status:** Pre-registered, not implemented, not run

**Created:** 4 September 2026

This document freezes B006 before any B006 code, B006 input-only warm-up data
build, research-period result, robustness result, or validation-period strategy
output exists. It is not a result artifact and does not authorize validation
inspection.

## Experiment Identity

| Field | Value |
| --- | --- |
| Experiment ID | B006 |
| Short name | 52-week-high proximity ranking |
| Author | Pradyot / Codex |
| Pre-registration date | 2026-09-04 |
| Research period | 2016-01-01 through 2022-12-31 |
| Validation holdout | 2023-01-01 through 2026-08-19, sealed |
| Prior related experiments | B001, B002, B003, B004, B005 |
| Phase 2 baseline slot | 3 of 3 |

## Hypothesis

A 52-week-high proximity ranking signal may capture behavioral anchoring around
salient prior price highs and improve return generation versus raw 60-session
relative momentum while preserving research-period risk, turnover, and
diversification discipline.

B006 is a return-ranking hypothesis. It is not a new risk overlay.

## Economic Reasoning

George and Hwang document that a stock's nearness to its 52-week high can
predict future returns and may contain information beyond conventional past
return momentum. The behavioral explanation is anchoring: investors may
underreact as prices approach a salient previous high.

B006 tests that ranking idea inside the existing V0 large-cap NSE framework.
Instead of asking which stocks rose most over the last 60 ordinary sessions, it
asks which stocks are trading closest to their own salient one-year high.

The Phase 2 interim finding records why the final baseline slot should target
return generation rather than another risk-control overlay. B004 and B005 both
reduced drawdown but failed return and Sharpe gates, and B005 doubled completed
round trips through continuous exposure resizing.

## External Basis

Primary source:

1. Thomas J. George and Chuan-Yang Hwang, "The 52-Week High and Momentum
   Investing", Journal of Finance 59(5), 2004, pp. 2145-2176, DOI:
   <https://doi.org/10.1111/j.1540-6261.2004.00695.x>.

Supporting India-specific evidence:

1. Rajan Raju, "The 52-Week High Effect and Momentum Investing: Evidence from
   India", SSRN:
   <https://ssrn.com/abstract=4587697>.

The India-specific evidence is supporting only. Its sample overlaps the
2016-2022 research window, so it is not used to choose B006 parameters or to
claim independent proof that B006 should work.

Contrary or cautionary evidence:

1. Graham Bornholt and Mirela Malin, "Is the 52-week high effect as strong as
   momentum? Evidence from developed and emerging market indices", Applied
   Financial Economics 21(18), 2011, pp. 1369-1379, RePEc:
   <https://ideas.repec.org/a/taf/apfiec/v21y2011i18p1369-1379.html>.

The contrary evidence is useful because B006 is a legitimate hypothesis, not a
known winner.

No other high-window length, threshold, breakout rule, volume confirmation,
trend filter, volatility overlay, or combined signal may be tested inside B006.

## Difference From Rejected Candidates

B006 is not B003 with a different lookback.

B003 ranks:

```text
60-session cumulative relative return
```

B006 ranks:

```text
current adjusted close / highest adjusted close during the preceding
52 calendar weeks, including the signal date
```

B006 is also not B004 or B005. It does not use:

```text
Nifty 100 TRI SMA regime filtering
binary risk-on/risk-off switching
realized-volatility exposure scaling
continuous exposure resizing
cash de-risking overlay
```

The portfolio wrapper stays close to B003 only to isolate the new return-ranking
input. Keeping weekly cadence, three positions, entry rank, hold rank,
execution, costs, and slippage unchanged makes the result interpretable.

## Universe And Data

| Field | Value |
| --- | --- |
| Universe rule | Frozen Phase 1 V0 20-stock Nifty 100 constituent sample |
| Universe version | `nifty100_v0_20_d037` |
| Research dataset version | `nifty100_v0_adjusted_ohlcv_d039` |
| B006 input dataset version | `nifty100_v0_52w_high_input_warmup_d074` |
| Benchmark | Nifty 100 TRI |
| Corporate-action treatment | Existing adjusted OHLCV dataset and unsupported held-security corporate-action guardrails, extended mechanically to B006 input-only warm-up history |
| Exclusions | Same frozen universe unless deterministic warm-up validation fails for a required symbol |

The research performance period does not change. B006 performance still begins
on 2016-01-01 and ends on 2022-12-31.

### Input-Only Warm-Up History

A valid 52-week-high signal requires pre-2016 history so the first eligible
2016 weekly signal has a complete trailing 52-calendar-week price window.

B006 therefore pre-registers an input-only warm-up extension:

```text
Warm-up purpose: signal construction only
Earliest required warm-up date: determined mechanically by the first ordinary
2016 signal date minus 52 calendar weeks
Warm-up P&L: none
Performance start: 2016-01-01
Validation holdout: unchanged and sealed
```

The warm-up extension must use the same deterministic market-data, processed
dataset, corporate-action, and validation standards as V0. If the warm-up
history cannot be built cleanly, B006 must be cancelled before implementation
or execution.

No B006 data build should begin until this pre-registration is merged.

## Strategy Rules

### Ranking Score

For each eligible stock `i` on weekly signal date `T`:

```text
PH52(i,T) =
adjusted_close(i,T)
/
max(adjusted_close(i,d) for ordinary sessions d where T - 364 calendar days <= d <= T)
```

Higher `PH52` is better.

The maximum adjusted close includes the signal date `T` because the decision is
made after the close of `T` and executed no earlier than the next eligible
session open. No observation after `T` may enter the score.

The denominator must be positive and must cover a complete trailing 52-calendar
week window. Missing required adjusted-close input must fail loudly. B006 must
not forward-fill, backfill, or use future observations to construct a score.

### Portfolio Rules

```text
Signal input: adjusted closes from the B006 input dataset
Ranking rule: highest PH52 score across eligible universe
Entry: rank <= 3
Hold: rank <= 6
Exit: rank > 6 or ineligible
Maximum positions: 3
Rebalance schedule: after close of final ordinary NSE research session of week
Execution: next eligible NSE session open
Sizing: equal weight
Direction: long/cash only
Leverage: none
Shorting: none
```

Ties are broken alphabetically by symbol, matching the deterministic ranking
style used by existing momentum signals.

## Execution And Costs

| Field | Value |
| --- | --- |
| Execution timing | Next eligible NSE session open after weekly close signal |
| Fill-price rule | Existing project open-price execution rule |
| Baseline slippage assumption | adverse deterministic slippage 0.05% |
| Cost profile | `ZERODHA_NSE_DELIVERY_2026_08` |
| Turnover measurement | Completed round trips per complete calendar year under existing turnover accounting |
| Unfilled-order policy | Existing deterministic unfilled-order policy; unfilled exits are carried and retried |

No changed cost, slippage, sizing, cadence, or execution assumption is part of
B006 baseline.

## B006-S015 Robustness Variant

`B006-S015` is pre-registered as the only B006 robustness row:

```text
Experiment ID: B006-S015
Same rules as B006
Only change: adverse deterministic slippage = 0.15%
```

Run `B006-S015` only if B006 passes every frozen baseline promotion gate.

It is not a rescue trial.

## Promotion Gates

B006 is eligible for robustness only if every research-period gate below
passes.

| Gate | Threshold | Reason |
| --- | --- | --- |
| Integrity gate | 0 accounting/state-integrity violations; 0 unexplained NAV differences; 0 unsupported held-security corporate-action breaches | Any accounting failure invalidates the result |
| Warm-up data gate | complete deterministic input-only 52-week warm-up for every required signal score | The score is invalid without a complete trailing high window |
| CAGR gate | strategy CAGR >= 0.137013 | Must at least match Nifty 100 TRI research-period CAGR |
| Drawdown gate | strategy maximum drawdown <= 0.379228 | Must not exceed Nifty 100 TRI research-period maximum drawdown |
| Sharpe gate | strategy Sharpe >= 0.837396 | Must at least match Nifty 100 TRI research-period Sharpe under project metric convention |
| Turnover gate | completed round trips <= 30 in every complete calendar year | Prevents excessive churn under Indian delivery-cost assumptions |
| Stock concentration gate | maximum stock positive contribution share <= 0.30 | No single stock may provide more than 30% of total positive realized completed-trade P&L |
| Calendar-year concentration gate | maximum calendar-year positive contribution share <= 0.35 | No single complete calendar year may provide more than 35% of total positive annual NAV gains |
| Minimum trade count | Report only; no separate pass/fail threshold | CAGR, Sharpe, turnover, and concentration gates already reject non-economic undertrading |

Benchmark thresholds are the already-recorded Phase 2 research-period Nifty 100
TRI thresholds over `2016-01-01..2022-12-31`.

There is no discretionary override. A high CAGR cannot compensate for a
drawdown, turnover, Sharpe, integrity, warm-up data, or concentration failure.

## Required Reporting Metrics

Every B006 report must include:

- net return;
- gross P&L before transaction costs, with slippage treatment explicitly
  labelled;
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
- 52-week-high lookback definition used;
- first signal date with complete 52-week-high input;
- count of missing or invalid PH52 scores;
- stock contribution concentration;
- calendar-year contribution concentration;
- direct B006-versus-B003 comparison using the same research period, universe,
  benchmark, cost profile, baseline slippage, cadence, and portfolio wrapper,
  including at minimum CAGR, maximum drawdown, Sharpe, turnover, transaction
  costs, and time invested.

## 52-Week-High Limitation

Every B006 report must state:

```text
52-WEEK-HIGH LIMITATION:
B006 TESTS A 52-WEEK-HIGH PROXIMITY RANKING SIGNAL ADAPTED FROM
GEORGE AND HWANG'S ANCHORING-BASED MOMENTUM EVIDENCE. THE V0 UNIVERSE
CONTAINS ONLY 20 LARGE-CAP NSE STOCKS, SO CROSS-SECTIONAL DISPERSION MAY BE
TOO LIMITED FOR THE EFFECT TO APPEAR. SUPPORTING INDIA-SPECIFIC EVIDENCE
OVERLAPS THE RESEARCH WINDOW AND IS NOT USED AS AN INDEPENDENT PARAMETER
SOURCE. DO NOT INTERPRET A GOOD RESULT AS PRECISE ESTIMATION OF A HIGH-WINDOW,
THRESHOLD, BREAKOUT, OR COMBINED-SIGNAL RULE.
```

## Explicitly Prohibited Variants

Do not test:

```text
NO 26-week high
NO 39-week high
NO 2-year high
NO "within 5% of high" threshold
NO breakout-above-high rule
NO volume confirmation
NO moving-average confirmation
NO alternative entry ranks
NO alternative hold ranks
NO position-count variants
NO rebalance-cadence variants
NO combination with B003 momentum
NO combination with B004 trend filter
NO combination with B005 volatility scaling
NO parameter sweep
NO B006-S015 unless B006 baseline passes every gate
```

## Expected Failure Modes

B006 fails or becomes economically unconvincing if:

- the 20-stock large-cap universe has too little cross-sectional dispersion for
  the 52-week-high effect to overcome costs and concentration;
- anchoring around prior highs is already efficiently reflected in this market
  segment;
- turnover breaches the annual turnover gate even with the unchanged 3/6
  hysteresis wrapper;
- return remains too dependent on one stock or one calendar year;
- the warm-up data extension cannot be built without changing the universe,
  corporate-action treatment, or research period;
- any implementation requires looking at validation-period strategy output.

## Stop Rules

Cancel B006 before implementation if the input-only warm-up dataset cannot be
built cleanly under deterministic V0 data and corporate-action rules.

Stop in research if any pre-registered gate fails.

Do not inspect validation-period strategy performance to rescue, tune, rank, or
reinterpret a failed B006 research-period candidate.

Do not change the 52-calendar-week lookback, inclusive signal-date rule,
ranking statistic, entry rank, hold rank, position count, weekly cadence, cost
profile, or slippage assumption after seeing B006 results.

## Output Artifacts

| Artifact | Path |
| --- | --- |
| Pre-registration | `docs/validation/B006_PREREGISTRATION_V0.md` |
| Ledger row | `experiments/ledger.csv` |
| Warm-up dataset artifact | `docs/validation/B006_INPUT_WARMUP_DATASET_V0.md` |
| Research result directory | `experiments/results/B006_research/` |
| Research report | `experiments/results/B006_research/phase1_report.md` until the report writer is renamed |
| Review or closeout note | `docs/phase2/B006_RESEARCH_REVIEW_V0.md` |

## Approval To Build Or Run

Before data build, implementation, or execution, confirm:

- [x] The experiment has a new ID.
- [x] The hypothesis is written before testing.
- [x] The economic reasoning is written before testing.
- [x] The difference from B001/B002/B003/B004/B005 is explicit.
- [x] The universe is frozen.
- [x] The required B006 input-only warm-up dataset is named before construction.
- [x] The research-period gates are written before testing.
- [x] The validation holdout remains sealed.
- [x] The experiment is not a rescue trial.

No B006 data build, implementation, or run should start until this
pre-registration is merged.
