# B005 Pre-Registration V0

**Status:** Pre-registered, not implemented, not run

**Created:** 4 September 2026

This document freezes B005 before any B005 code, research-period result,
robustness result, or validation-period strategy output exists. It is not a
result artifact and does not authorize validation inspection.

## Experiment Identity

| Field | Value |
| --- | --- |
| Experiment ID | B005 |
| Short name | Momentum volatility-scaled exposure |
| Author | Pradyot / Codex |
| Pre-registration date | 2026-09-04 |
| Research period | 2016-01-01 through 2022-12-31 |
| Validation holdout | 2023-01-01 through 2026-08-19, sealed |
| Prior related experiments | B001, B002, B003, B004 |
| Phase 2 baseline slot | 2 of 3 |

## Hypothesis

A realized-volatility exposure overlay, adapted from Barroso and Santa-Clara's
risk-managed momentum mechanism, may reduce the downside weakness of the frozen
B003 weekly relative-momentum/hysteresis strategy while preserving sufficient
research-period return, risk-adjusted performance, turnover control, and return
diversification.

## Economic Reasoning

Barroso and Santa-Clara document that momentum risk is highly time-varying and
predictable from recent realized variance. Their risk-managed momentum method
scales exposure using prior daily momentum returns, targeting constant
volatility; the published paper uses prior 6 months of daily returns and a 12%
annualized volatility target.

B005 tests the same economic mechanism at the portfolio-exposure layer:
momentum exposure should be reduced when the realized volatility of the
underlying momentum strategy is high, because high recent momentum volatility
may signal a less attractive crash-risk environment. This is a risk-management
hypothesis, not a new stock-ranking hypothesis.

## External Basis

Primary source:

1. Pedro Barroso and Pedro Santa-Clara, "Momentum has its moments", Journal of
   Financial Economics 116(1), 2015, pp. 111-120, DOI:
   <https://doi.org/10.1016/j.jfineco.2014.11.010>.

Implementation parameters taken from the paper before testing:

```text
Realized-volatility lookback: prior 6 months of daily returns
Repository adaptation: 126 ordinary NSE sessions
Target volatility: 12% annualized
```

No other lookback, volatility target, cap, floor, smoothing method, or
volatility estimator may be tested inside B005.

## Difference From Rejected Candidates

B005 is not B004 with different trend-filter parameters.

It does not use:

```text
Nifty 100 TRI SMA length
TRI > SMA risk-on rule
TRI <= SMA risk-off rule
binary market-regime switching
SMA threshold variants
SMA cadence variants
```

B005 also does not change the B003 stock-ranking family:

```text
lookback = 60 sessions
entry_rank <= 3
hold_while_rank <= 6
maximum positions = 3
weekly rebalance
```

The new mechanism is continuous exposure scaling from trailing realized
volatility of the underlying momentum strategy. It is a portfolio-risk overlay,
not a momentum lookback, position-count, rebalance-frequency, slippage, or
market-trend rescue trial.

## Universe And Data

| Field | Value |
| --- | --- |
| Universe rule | Frozen Phase 1 V0 20-stock Nifty 100 constituent sample |
| Universe version | `nifty100_v0_20_d037` |
| Dataset version | `nifty100_v0_adjusted_ohlcv_d039` |
| Benchmark | Nifty 100 TRI |
| Corporate-action treatment | Existing adjusted OHLCV dataset and unsupported held-security corporate-action guardrails |
| Exclusions | Same as B003; no new exclusions |

The universe and dataset do not change in B005.

## Strategy Rules

### Underlying Momentum Reference

B005 uses the frozen B003 weekly momentum/hysteresis rules as the unscaled
reference:

```text
Signal input: adjusted closes from the frozen V0 dataset
Momentum lookback: 60 ordinary trading sessions
Ranking rule: highest 60-session relative momentum across eligible universe
Entry: rank <= 3
Hold: rank <= 6
Exit: rank > 6 or ineligible
Maximum positions: 3
Rebalance schedule: after close of final ordinary NSE research session of week
Execution: next eligible NSE session open
```

### Realized-Volatility Estimate

At each weekly decision date `T`, compute the realized volatility of the
unscaled B003 reference strategy from prior daily simple returns:

```text
r_ref(d) = daily simple return of the unscaled B003 reference NAV
lookback_sessions = 126 ordinary NSE sessions
annualization_sessions = 252

realized_vol(T) =
sqrt((annualization_sessions / lookback_sessions) *
     sum(r_ref(d)^2 for the 126 ordinary sessions ending at T))
```

The return for date `T` may be used only because the decision is made after the
close of `T` and executed no earlier than the next eligible session open. No
return after `T` may enter the estimate.

The calculation uses squared simple returns and does not subtract a sample mean.

### Exposure Multiplier

The target annualized volatility is frozen:

```text
target_volatility = 0.12
```

The B005 exposure multiplier is:

```text
raw_multiplier(T) = target_volatility / realized_vol(T)
exposure_multiplier(T) = min(1.0, raw_multiplier(T))
```

If `realized_vol(T)` is zero, missing, non-finite, or has fewer than 126 prior
ordinary-session reference returns:

```text
exposure_multiplier(T) = 0.0
portfolio target = cash
new entries = prohibited
```

### Cash-Constrained Adaptation

Barroso and Santa-Clara study a self-financing long-short momentum factor whose
exposure can be scaled above or below one. This repository's current strategy
surface is long/cash delivery-style equity exposure with no margin or short
book.

B005 therefore caps exposure at 100% of NAV:

```text
maximum exposure multiplier = 1.0
minimum exposure multiplier = 0.0
no leverage
no shorting
unused NAV remains cash
```

This cap is a feasibility constraint of the project implementation, not a
searched performance parameter.

### Portfolio Targeting

On each weekly rebalance:

1. Determine the B003 desired symbol set using the frozen B003 ranking and
   hysteresis rules.
2. Compute `exposure_multiplier(T)`.
3. Target total invested value:

```text
target_invested_value = NAV(T) * exposure_multiplier(T)
```

4. Allocate target invested value equally across desired symbols.
5. If the desired symbol set is empty or exposure multiplier is zero, target
   cash.
6. Schedule required reductions, exits, and entries for the next eligible NSE
   session open.

Exits and exposure reductions execute before entries and exposure increases.

### Missing Data Handling

Required input observations must be present for:

- symbol adjusted close values used by B003 ranking;
- next-open execution prices;
- unscaled B003 reference NAV returns used by the volatility estimator.

Missing required input data must fail loudly. B005 must not forward-fill,
backfill, or use future observations to create either momentum ranks or
realized-volatility estimates.

## Execution And Costs

| Field | Value |
| --- | --- |
| Execution timing | Next eligible NSE session open after weekly close signal |
| Fill-price rule | Existing project open-price execution rule |
| Baseline slippage assumption | adverse deterministic slippage 0.05% |
| Cost profile | `ZERODHA_NSE_DELIVERY_2026_08` |
| Turnover measurement | Completed round trips per complete calendar year under existing turnover accounting |
| Unfilled-order policy | Existing deterministic unfilled-order policy; unfilled exits/reductions are carried and retried |

No changed cost or slippage assumption is part of B005 baseline.

## B005-S015 Robustness Variant

`B005-S015` is pre-registered as the only B005 robustness row:

```text
Experiment ID: B005-S015
Same rules as B005
Only change: adverse deterministic slippage = 0.15%
```

Run `B005-S015` only if B005 passes every frozen baseline promotion gate.

It is not a rescue trial.

## Promotion Gates

B005 is eligible for robustness only if every research-period gate below passes.

| Gate | Threshold | Reason |
| --- | --- | --- |
| Integrity gate | 0 accounting/state-integrity violations; 0 unexplained NAV differences; 0 unsupported held-security corporate-action breaches | Any accounting failure invalidates the result |
| CAGR gate | strategy CAGR >= 0.137013 | Must at least match Nifty 100 TRI research-period CAGR |
| Drawdown gate | strategy maximum drawdown <= 0.379228 | Must not exceed Nifty 100 TRI research-period maximum drawdown |
| Sharpe gate | strategy Sharpe >= 0.837396 | Must at least match Nifty 100 TRI research-period Sharpe under project metric convention |
| Turnover gate | completed round trips <= 30 in every complete calendar year | Prevents excessive churn under Indian delivery-cost assumptions |
| Stock concentration gate | maximum stock positive contribution share <= 0.30 | No single stock may provide more than 30% of total positive realized completed-trade P&L |
| Calendar-year concentration gate | maximum calendar-year positive contribution share <= 0.35 | No single complete calendar year may provide more than 35% of total positive annual NAV gains |
| Minimum trade count | Report only; no separate pass/fail threshold | A volatility-scaling overlay can legitimately de-risk to cash, and CAGR/Sharpe/concentration gates already reject non-economic undertrading |

Benchmark thresholds are the already-recorded Phase 2 research-period Nifty 100
TRI thresholds over `2016-01-01..2022-12-31`.

There is no discretionary override. A high CAGR cannot compensate for a
drawdown, turnover, Sharpe, integrity, or concentration failure.

## Required Reporting Metrics

Every B005 report must include:

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
- realized-volatility lookback used;
- target volatility used;
- minimum, maximum, mean, and median exposure multiplier;
- number of weekly exposure changes;
- percentage of research sessions at 0 exposure, between 0 and 1 exposure, and
  at 1 exposure;
- stock contribution concentration;
- calendar-year contribution concentration;
- direct B005-versus-B003 comparison using the same research period, universe,
  dataset, benchmark, cost profile, and baseline slippage, including at minimum
  CAGR, maximum drawdown, Sharpe, turnover, transaction costs, and time
  invested.

## Noisy-Realized-Volatility Limitation

Every B005 report must state:

```text
REALIZED-VOLATILITY LIMITATION:
B005 USES A 126-SESSION REALIZED-VOLATILITY ESTIMATE ADAPTED FROM
BARROSO AND SANTA-CLARA'S SIX-MONTH MOMENTUM RISK-MANAGEMENT METHOD.
THE 2016-2022 RESEARCH WINDOW PROVIDES A LIMITED NUMBER OF INDEPENDENT
HIGH-VOLATILITY MOMENTUM EPISODES, AND REALIZED VOLATILITY IS ITSELF NOISY.
DO NOT INTERPRET A GOOD RESULT AS PRECISE ESTIMATION OF AN OPTIMAL VOLATILITY
TARGET, LOOKBACK, OR EXPOSURE-SCALING RULE.
```

## Expected Failure Modes

B005 fails or becomes economically unconvincing if:

- the exposure cap spends too much time below full investment and CAGR fails;
- realized volatility is noisy and reduces exposure after losses rather than
  before them;
- turnover from resizing positions breaches the annual turnover gate;
- reduced exposure improves drawdown but fails Sharpe or CAGR;
- return remains too dependent on one stock or one calendar year;
- the long/cash adaptation loses the core self-financing feature of the
  original Barroso/Santa-Clara long-short factor;
- any implementation requires looking at validation-period strategy output.

## Stop Rules

The experiment must stop in research if any pre-registered gate fails.

Do not inspect validation-period strategy performance to rescue, tune, rank, or
reinterpret a failed B005 research-period candidate.

Do not change the 126-session lookback, 12% target, no-leverage cap, weekly
cadence, B003 ranking rules, cost profile, or slippage assumption after seeing
B005 results.

## Output Artifacts

| Artifact | Path |
| --- | --- |
| Pre-registration | `docs/validation/B005_PREREGISTRATION_V0.md` |
| Ledger row | `experiments/ledger.csv` |
| Research result directory | `experiments/results/B005_research/` |
| Research report | `experiments/results/B005_research/phase1_report.md` until the report writer is renamed |
| Review or closeout note | `docs/phase2/B005_RESEARCH_REVIEW_V0.md` |

## Approval To Run

Before execution, confirm:

- [x] The experiment has a new ID.
- [x] The hypothesis is written before testing.
- [x] The economic reasoning is written before testing.
- [x] The difference from B001/B002/B003/B004 is explicit.
- [x] The universe and data version are frozen or named.
- [x] The research-period gates are written before testing.
- [x] The validation holdout remains sealed.
- [x] The experiment is not a rescue trial.

No B005 implementation or run should start until this pre-registration is
merged.
