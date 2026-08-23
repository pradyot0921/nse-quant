# Phase 1 — First Vertical Slice

**Project:** NSE Quant Research and Trading System  
**Phase:** 1  
**Objective:** Produce one fully reconciled end-to-end research/backtest path  
**Starting capital:** ₹50,000 simulated  
**Market:** NSE cash equity delivery  
**Status:** IN PROGRESS  
**Last updated:** 19 August 2026

---

## 1. Phase 1 Objective

Phase 1 is successful when the project can take validated NSE daily data through the full pipeline:

```text
Raw NSE Data
    ↓
Validated / Normalised Data
    ↓
Corporate-Action Adjustment
    ↓
Frozen 20-Stock Universe
    ↓
B001 Signal
    ↓
T+1 Open Simulated Execution
    ↓
Indian Trading Costs
    ↓
Cash + Holdings Accounting
    ↓
Portfolio NAV
    ↓
Nifty 100 TRI Comparison
    ↓
Reconciled Report
```

The objective is **not** to make B001 profitable.

The objective is to prove that every rupee, share, date, signal, and adjustment can be explained.

---

## 2. Build Order

Phase 1 must be implemented in this order:

1. `costs/india_equity.py`
2. cost-model unit tests
3. validation against a real broker contract note / funds statement when available
4. corporate-action module
5. corporate-action tests and visual verification
6. NSE UDiFF loader
7. raw-data validation
8. fixed-universe selection script
9. frozen universe file
10. explicit day-loop backtest engine
11. portfolio and cash accounting
12. B001 strategy
13. benchmark ingestion
14. reporting
15. one manually reconciled trade
16. full B001 run
17. Phase 1 review

Do not start strategy optimisation before the accounting pipeline passes.

---

## 3. Initial Repository Structure

Use a deliberately small repository.

```text
nse-quant/
│
├── README.md
├── pyproject.toml
├── .gitignore
│
├── docs/
│   ├── PHASE_0_PROJECT_SPEC.md
│   ├── PHASE_1_VERTICAL_SLICE.md
│   └── DECISIONS.md
│
├── config/
│   └── settings.example.toml
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
│
├── universes/
│   ├── selection_rule_v0.md
│   └── nifty100_v0_20.csv
│
├── experiments/
│   └── ledger.csv
│
├── src/
│   └── nse_quant/
│       ├── costs/
│       │   └── india_equity.py
│       │
│       ├── data/
│       │   ├── nse_udiff.py
│       │   ├── corporate_actions.py
│       │   └── validation.py
│       │
│       ├── backtest/
│       │   ├── engine.py
│       │   ├── portfolio.py
│       │   ├── orders.py
│       │   └── fills.py
│       │
│       ├── strategies/
│       │   └── b001_momentum.py
│       │
│       └── reporting/
│           └── performance.py
│
└── tests/
    ├── costs/
    ├── data/
    ├── backtest/
    └── strategies/
```

No database server, dashboard, broker adapter, LLM agent, or microservice is required in Phase 1.

---

## 4. Task 1 — India Equity Cost Engine

### 4.1 Goal

Create:

```text
src/nse_quant/costs/india_equity.py
```

The module must calculate transaction costs deterministically using `Decimal`.

Do not use binary `float` for settlement-style monetary arithmetic.

Where a rule requires rounding to the nearest rupee, use explicit half-up rounding:

```python
from decimal import Decimal, ROUND_HALF_UP

amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
```

Do not rely on `Decimal.quantize()` defaults. Default half-even rounding can turn ₹10.50 into ₹10, which is incorrect when the applicable rule requires half-up rounding.

### 4.2 Design requirements

The cost engine should accept trade/fill information and return a structured breakdown.

Example conceptual output:

```text
Buy turnover
Sell turnover
Brokerage
STT
Exchange transaction charge
SEBI turnover charge
GST
Stamp duty
DP charges
Total cost
```

### 4.3 Daily aggregation

Costs must support day-level aggregation.

This matters because broker/depository charges may depend on:

- side;
- daily turnover;
- sold symbols;
- number of settlements;
- broker/account profile.

For the current Zerodha reference profile, DP charging is per sold stock per day under a normal single-settlement case, not per sell fill.

For V0 delivery STT:

```text
STT_buy  = ROUND_HALF_UP(sum(daily BUY turnover)  × STT rate)
STT_sell = ROUND_HALF_UP(sum(daily SELL turnover) × STT rate)
```

Round once per side for the day. Do not round each fill independently and then sum.

This convention must be validated against the real contract note. If a broker documents a different aggregation method, encode that difference in its named cost profile.

### 4.3.1 Fill-level cost allocation for reports

The daily aggregate remains the authoritative accounting unit.

Fill-level and symbol-level cost rows used in trade logs, manual reconciliation, and reports are **allocations**, not broker-settlement facts.

Allocation rule for the initial Zerodha delivery profile:

- DP charges are assigned directly to the sold symbol.
- If the same symbol has multiple same-day sell fills, that symbol's DP charge is allocated across those sell fills pro-rata by that symbol's same-day sell turnover.
- Buy-side STT is allocated across buy fills pro-rata by buy turnover.
- Sell-side STT is allocated across sell fills pro-rata by sell turnover.
- Stamp duty is allocated across buy fills pro-rata by buy turnover.
- Brokerage, exchange transaction charges, SEBI charges, and GST are allocated across all fills pro-rata by total turnover.

Every allocated component must sum back exactly to the authoritative daily component total.

Reports and trade logs must label these values as:

```text
REPORTING ALLOCATION; DAILY TOTAL IS AUTHORITATIVE
```

Do not use allocated fill-level charges to re-create cash accounting when the daily charge total is available.

### 4.4 Cost profile

Do not put unexplained global constants into code.

Use named, dated profiles, for example:

```text
ZERODHA_NSE_DELIVERY_2026_08
```

Current reference assumptions checked directly against Zerodha's published schedule on 19 August 2026:

```text
Delivery brokerage:            ₹0
STT:                           0.1% buy + 0.1% sell
NSE transaction charge:        0.00307%
SEBI turnover charge:          ₹10 per crore
GST:                           18% on brokerage + exchange + SEBI charges
Stamp duty:                    0.015% on buy side
DP male-primary pre-GST base:   ₹13.00 per sold stock/day
DP female-primary pre-GST base: ₹12.75 per sold stock/day
```

These are implementation reference values, not permanent assumptions.

### 4.4.1 Retrospective use of the 2026 schedule

The first historical backtests will deliberately apply the **2026 reference fee schedule to older market data**.

This answers:

> Would the historical strategy have survived approximately today's cost structure?

It does **not** reproduce the actual historical fee regime. STT and other statutory/broker charges have changed over time.

Reports using this model must state:

```text
COST MODEL: CURRENT 2026 REFERENCE SCHEDULE APPLIED RETROSPECTIVELY
HISTORICAL FEE RECONSTRUCTION: NO
```

Historical fee schedules may be implemented later only if the research question requires them.

### 4.5 GST base

For the current Zerodha reference profile, GST applies to:

```text
brokerage + exchange transaction charges + SEBI charges
```

Do **not** include stamp duty or DP charges in the GST base.

DP charges are calculated from the aggregate pre-GST DP base for distinct sold symbols, then GST is applied once to that aggregate. DP GST remains inside the DP charge total and is not included in the normal trading-charge GST component.

### 4.6 Slippage

Do not include slippage in the statutory fee calculator.

Slippage must alter the simulated fill price and must be adverse in the initial deterministic model:

```text
BUY fill  = reference price × (1 + slippage_rate)
SELL fill = reference price × (1 - slippage_rate)
```

with `slippage_rate >= 0`.

Do not use symmetric/random slippage that averages to zero in V0/V1.

The fee calculator then operates on the resulting simulated turnover.

Initial frozen slippage assumptions:

```text
Baseline adverse deterministic slippage:   0.05%
Robustness adverse deterministic slippage: 0.15%
```

The 0.15% robustness run is a separate pre-registered parameter specification and must not be chosen after seeing baseline results.

### 4.7 Income tax

Personal income tax is not part of `india_equity.py`.

---

## 5. Cost-Engine Tests

These tests must exist before data research begins.

### 5.1 Zero-fill test

No fills:

```text
total turnover = ₹0
total cost = ₹0
```

### 5.2 Flat-price round trip

Buy and sell at the same price.

Gross P&L:

```text
₹0
```

Net P&L:

```text
-negative transaction costs
```

Ending capital must equal starting capital minus charges.

### 5.3 Same-symbol DP aggregation

Sell the same stock twice on the same day.

Expected:

```text
one DP charge
```

### 5.4 Multi-symbol DP aggregation

Sell two distinct stocks on the same day.

Expected:

```text
two DP charges
```

### 5.5 Female-primary DP profile

The female-primary DP profile should use the dated pre-GST base and apply GST after daily sold-symbol aggregation:

```text
one sold stock:  ₹12.75 × 1.18 = ₹15.05
two sold stocks: ₹25.50 × 1.18 = ₹30.09
```

### 5.6 Buy-only DP test

A purchase should not produce a delivery sell DP charge.

### 5.7 Stamp-duty side test

Stamp duty in the reference delivery profile must apply on the buy side only.

### 5.8 STT rounding test

The engine must reproduce the broker/exchange rounding policy used by the chosen reference profile.

For any rule requiring nearest-rupee half-up rounding, the test must verify the boundary explicitly. Example:

```text
₹10.50 → ₹11
```

The implementation must pass `ROUND_HALF_UP` explicitly rather than relying on the Decimal context/default.

Small trades may round STT to zero under nearest-rupee half-up rounding. This assumption must be checked against a real contract note when available.

### 5.9 STT aggregation test

Create multiple BUY fills and multiple SELL fills on the same trading day.

The engine must:

- sum all delivery BUY turnover for the day and round buy-side STT once;
- sum all delivery SELL turnover for the day and round sell-side STT once;
- not round STT independently per fill.

### 5.10 GST-base exclusion test

The test must prove that:

```text
GST base excludes stamp duty
GST base excludes DP charges
DP charge is not taxed twice
```

### 5.11 Daily total invariant

The daily `total_cost` must equal the sum of:

- brokerage;
- STT;
- exchange transaction charges;
- SEBI turnover charges;
- GST;
- stamp duty;
- DP charges.

### 5.12 Allocation sum-back invariant

Allocated fill-level components must sum back exactly to the authoritative daily component totals.

### 5.13 Invalid data

Reject:

- zero quantity;
- negative quantity;
- zero price;
- negative price;
- blank symbol;
- mixed trade dates passed to a single-day calculator where not supported.

---

## 6. Real-World Cost Validation

Before proceeding past the cost module, compare the output with a real delivery trade record if available.

For Zerodha, note:

- contract notes contain exchange/trading charges;
- DP charges are posted separately to the funds statement.

Acceptance target:

```text
Absolute difference in daily total charges:
≤ ₹1
```

Do not require paise-perfect agreement on every individual component. Brokers and exchanges may round or aggregate at different points in the calculation.

Component-level differences should still be inspected for diagnosis, but the formal acceptance criterion is the daily total.

Any daily-total mismatch greater than ₹1 must be investigated and explained before proceeding.

---

## 7. Task 2 — Corporate-Action Module

Create:

```text
src/nse_quant/data/corporate_actions.py
```

### 7.1 Mandatory V1 action types

Support at minimum:

- split;
- bonus.

Other events should be surfaced as warnings rather than silently ignored if they may affect price continuity.

### 7.2 Input

Use NSE corporate-action information containing fields such as:

- symbol;
- company;
- purpose;
- ex-date;
- record date;
- face value where relevant.

### 7.3 Output

The module should be capable of producing:

- parsed event type;
- event ratio / factor;
- effective ex-date;
- adjustment factor;
- audit record explaining the adjustment.

### 7.4 No guessing

If the purpose text cannot be parsed safely:

```text
UNSUPPORTED_CORPORATE_ACTION
```

The system should fail loudly or quarantine the event for manual review.

### 7.5 Adjustment convention

Document whether the project uses backward-adjusted historical prices and how OHLC and volume are transformed.

The convention must remain consistent throughout the research dataset.

### 7.6 Test cases

Include at least:

- one split;
- one bonus;
- one unaffected security;
- one malformed/unsupported action.

---

## 8. Corporate-Action Visual Validation

Before trusting the module:

1. identify a security with a known split/bonus;
2. plot raw close around the ex-date;
3. plot adjusted close;
4. confirm the mechanical discontinuity is removed;
5. inspect OHLC and volume adjustment;
6. store the validation result in project notes.

A spectacular strategy result obtained before this validation is not trustworthy.

---

## 9. Task 3 — NSE UDiFF Loader

Create:

```text
src/nse_quant/data/nse_udiff.py
```

### 9.1 Source

Use NSE:

**CM-UDiFF Common Bhavcopy Final**

### 9.2 Raw storage

Raw downloads are immutable.

Suggested path:

```text
data/raw/nse/cm_udiff/YYYY/MM/
```

Example:

```text
data/raw/nse/cm_udiff/2026/08/BhavCopy_....zip
```

### 9.3 Processed format and numeric types

The processed dataset may use CSV or Parquet initially.

Prefer a format that preserves:

- exact date types;
- reproducible schema;
- reasonable read speed.

Before data enters execution, accounting, or NAV calculations, convert all monetary price fields to `Decimal`, including:

- open;
- high;
- low;
- close;
- any simulated execution/reference price.

Do not carry binary floating-point prices into the backtester.

Volumes and integer counts may remain integer types.

Do not add a database server in Phase 1.

### 9.4 Loader responsibilities

- locate/download source data;
- retain raw file;
- unzip/read;
- validate schema;
- normalise column names;
- select relevant cash-equity rows;
- preserve identifiers;
- convert date/numeric columns;
- write clean daily table;
- log rejected rows.

---

## 10. Task 4 — Data Validation

Create:

```text
src/nse_quant/data/validation.py
```

Checks should include:

### Price consistency

```text
high >= max(open, close, low)
low <= min(open, close, high)
price > 0
```

### Row integrity

- unique symbol/date where expected;
- required fields present;
- valid series;
- no duplicate security/date rows.

### Calendar integrity

- known NSE non-trading days allowed;
- accidental missing trading days flagged.

### Return anomalies

Flag rather than automatically delete extreme daily moves.

An extreme move may be:

- a real market event;
- a corporate action;
- bad data.

---

## 11. Task 5 — Freeze the 20-Stock Universe

Create:

```text
universes/selection_rule_v0.md
universes/nifty100_v0_20.csv
```

### 11.1 Rule first

Write the selection rule before seeing B001 performance.

### 11.2 Freeze metadata

The universe file should contain at least:

```text
symbol
company_name
selection_date
selection_rule_version
notes
```

### 11.3 Immutable-after-test rule

Once B001 has run:

- do not replace a stock because it “looks bad”;
- do not remove a stock because it hurts performance;
- do not change the liquidity threshold and reuse the same experiment ID.

Any such modification becomes a new universe version and new experiment.

---

## 12. Task 6 — Explicit Day-Loop Backtester

Create:

```text
src/nse_quant/backtest/engine.py
```

The first engine should iterate trading day by trading day.

Conceptual order:

```text
START DAY T
    ↓
Load current portfolio state
    ↓
Apply today's market/open fills scheduled from T-1 signals
    ↓
Calculate fees
    ↓
Update cash and holdings
    ↓
Mark holdings using today's data
    ↓
At close, calculate signals using data available through T
    ↓
Generate orders for T+1
    ↓
Write audit log
END DAY T
```

### 12.1 State

At minimum maintain:

- cash;
- positions;
- average/lot cost as needed;
- pending orders;
- fills;
- realised P&L;
- unrealised P&L;
- NAV;
- transaction costs;
- exposure.

### 12.2 Daily NAV invariant

All prices entering the backtester must already be `Decimal`.

After the day's fills and mark-to-market, quantize monetary values consistently to the documented accounting precision and assert exact `Decimal` equality:

```text
NAV == cash + Σ(quantity × close for every holding)
```

The invariant must hold **every trading day**, not only at the end of the backtest.

Do not introduce an arbitrary float tolerance to make the invariant pass.

On breach:

```text
HALT RUN
WRITE DIAGNOSTIC STATE
DO NOT CONTINUE
```

If a held security has no valid close for valuation, V0 must halt rather than silently forward-fill.

This daily check is required because an intermediate accounting error can corrupt drawdown, exposure, and path-dependent metrics even if the final NAV later happens to reconcile.

### 12.3 No impossible fills

The engine must not assume a trade can occur before the information that generated it existed.

### 12.4 Gap-aware entries, full exits, and unfilled-exit retry

A close(T) signal creates an order intent. Entry quantity is not final until the actual T+1 simulated fill price is known.

At open(T+1), for entries:

1. apply the adverse slippage model to the reference open;
2. process scheduled exits before new entries;
3. calculate available cash;
4. calculate the whole-share quantity affordable at the actual simulated fill price including estimated buy-side charges;
5. round quantity down;
6. reduce quantity further if required so cash does not become negative;
7. if even one share is unaffordable, skip the entry;
8. log the outcome.

Required entry statuses should include concepts equivalent to:

```text
FILLED_AS_INTENDED
GAP_RESIZED
INSUFFICIENT_CASH_SKIP
```

For exits:

- always submit/simulate the **full held quantity**;
- never resize an exit merely because the open price changed;
- never deliberately create a stub holding from an exit signal.

If the modeled execution cannot fill the exit at all because there is no executable trade at the open, including circuit/no-trade conditions:

```text
EXIT_UNFILLED
CARRY_POSITION_FORWARD
RETRY_NEXT_ELIGIBLE_SESSION
```

The full position remains held and the exit intent remains pending until the next session in which the execution model permits a fill.

While carried, the position remains part of exposure and NAV. If there is no valid close for valuation, the missing-valuation kill switch halts the run.

The backtester must never fund an unexpected T+1 gap with implicit leverage.

---

## 13. Mandatory Three-Trade Hand Test

Before running B001 on years of data, construct a synthetic scenario with three trades.

Manually calculate:

- starting cash;
- entry quantities;
- entry cost;
- applicable charges;
- sale proceeds;
- exit charges;
- final cash;
- holdings;
- realised P&L;
- final NAV.

The engine result must match the manual calculation using the same `Decimal` price and money conventions as production backtests.

The synthetic execution tests must also include:

- one entry that gaps above the sizing reference and is resized downward;
- one full exit that is temporarily unfillable and is carried/retried without creating a stub holding.

This test is more important than a fast backtest.

---

## 14. Task 7 — B001 Baseline

Create:

```text
src/nse_quant/strategies/b001_momentum.py
```

### 14.1 Purpose

B001 is a pipeline baseline.

Do not interpret success as proof of a durable edge.

### 14.2 Hypothesis

A pre-specified form of relative strength may persist sufficiently to produce a measurable ranking signal among liquid large-cap NSE stocks.

### 14.3 Pre-registered initial specifications

All three specifications below must be entered into `experiments/ledger.csv` **before B001 is executed**.

All six Phase 1 ledger rows use the same pre-registered date split:

```text
research_period:   2016-01-01 through 2022-12-31, inclusive
validation_period: 2023-01-01 through 2026-08-19, inclusive
```

The validation period is a one-time holdout for Phase 1 B001/B002/B003
evaluation. Once inspected, it is contaminated for future selection or
parameter tuning. Newly accumulated market data after 2026-08-19 is the next
unseen frontier unless a later decision explicitly labels reused data as
previously inspected.

#### B001 — 3-position weekly momentum baseline

```text
Lookback:
60 trading sessions

Signal:
past return ending at T close, using only information available through T

Rebalance frequency:
weekly

Rebalance observation:
final NSE trading session of each week, after that session's close

Ranking:
rank eligible stocks by signal at the weekly rebalance observation

Portfolio:
maximum 3 positions

Entry:
enter names ranked 1–3
weekly signal at T close → earliest fill next NSE trading session at open

Exit:
at the next weekly rebalance, exit a holding if it is no longer ranked 1–3 or becomes ineligible

Forced maximum hold:
none

Direction:
long/cash
```

#### B002 — 2-position cost/concentration variant

B002 is identical to B001 except:

```text
Portfolio:
maximum 2 positions

Entry:
enter names ranked 1–2

Exit:
exit if no longer ranked 1–2 or becomes ineligible
```

B002 is a separate trial because fixed DP costs and concentration interact with ₹50,000 starting capital.

#### B003 — Pre-registered hysteresis response

B003 is registered before B001 results are known.

```text
Lookback:
60 trading sessions

Rebalance:
weekly

Portfolio:
maximum 3 positions

Entry:
rank 3 or better

Hold:
continue holding while rank is 6 or better

Exit:
rank below 6 or ineligible

Execution:
next NSE trading session open

Direction:
long/cash
```

If B001 exceeds the turnover mandate, mark B001 as failed on turnover and then run B003. Do not choose a different hysteresis threshold after seeing B001.

B003 remains a counted, pre-registered specification even if B001 passes and B003 is never executed.

#### Turnover evaluation for B001/B002/B003

```text
Engine behaviour:
never block a trade because of the annual ceiling

PASS:
every complete calendar year has ≤ 30 completed round trips

FAIL:
any complete calendar year has > 30 completed round trips

Partial first/last calendar years:
report separately
exclude from PASS/FAIL
do not annualise
```

### 14.4 No broad optimisation

Do not immediately test dozens of lookbacks, rebalance frequencies, ranking thresholds, stops, filters, or hysteresis bands.

Run only the pre-registered specifications in their defined order and record every result.

---

## 15. Experiment Ledger

Create:

```text
experiments/ledger.csv
```

Suggested columns:

```text
experiment_id
created_at
status
hypothesis
universe_version
data_version
strategy
parameters
position_count
entry_rule
exit_rule
turnover_limit
cost_profile
slippage_model
research_period
validation_period
benchmark
cagr
max_drawdown
sharpe
sortino
calmar
turnover
net_return
notes
```

Possible statuses:

```text
PLANNED
RUNNING
FAILED_ENGINE
REJECTED
VALIDATION_PENDING
CANDIDATE
```

Never delete failed trials.

---

## 16. Benchmark Data

The report must compare the strategy with:

**Nifty 100 TRI**

### 16.1 Primary source

Use:

**NSE Indices Historical Data → Total returns Index Values → Nifty 100**

Source page:

```text
https://www.niftyindices.com/reports/historical-data
```

The benchmark series must be date-aligned with the strategy NAV.

Handle:

- missing benchmark dates;
- start-date normalisation;
- reinvestment already reflected in TRI;
- comparable CAGR period.

### 16.2 Fallback if TRI retrieval blocks development

If the official TRI series cannot be retrieved during an engineering run, use a clearly labelled approximate fallback built from:

- official Nifty 100 price-index history; plus
- separately sourced historical dividend-yield information from NSE Indices.

Every output using the fallback must show:

```text
BENCHMARK: APPROXIMATE NIFTY 100 TOTAL-RETURN PROXY
OFFICIAL TRI SERIES: UNAVAILABLE FOR THIS RUN
USE FOR STRATEGY PROMOTION: NO
```

The fallback exists only so benchmark-ingestion problems do not block the vertical slice.

Do not use an approximate benchmark to approve or reject a strategy for paper/live promotion.

---

## 17. Reporting

Create:

```text
src/nse_quant/reporting/performance.py
```

Minimum report:

### Portfolio

- starting capital;
- ending capital;
- gross P&L;
- transaction costs;
- slippage;
- net P&L;
- CAGR;
- volatility;
- maximum drawdown;
- Sharpe;
- Sortino;
- Calmar;
- number of completed round trips;
- turnover;
- average holding period;
- percentage time invested;
- win rate;
- profit factor;
- average winning trade;
- average losing trade;
- average win / average loss ratio;
- expectancy per completed trade.

### Benchmark

- benchmark start/end;
- benchmark CAGR;
- benchmark volatility;
- benchmark max drawdown where calculated consistently.

### Relative

- CAGR difference;
- strategy maximum drawdown;
- benchmark maximum drawdown over the identical period;
- drawdown difference in percentage points;
- drawdown improvement/worsening relative to benchmark drawdown;
- research drawdown gate:

```text
PASS if strategy max drawdown is no worse than benchmark max drawdown
FAIL if strategy max drawdown is worse than benchmark max drawdown
```

- risk-adjusted comparison;
- cost drag.

The 15% future live-account drawdown limit is **not** used as a historical research gate.

### Research warnings

Always show:

```text
SURVIVORSHIP-BIASED V0 UNIVERSE
NOT POINT-IN-TIME
NOT LIVE-TRADING VALIDATION
SMALL SAMPLE: 20 STOCKS / 2–3 POSITIONS / ONE FIXED UNIVERSE
FEW INDEPENDENT BETS — ESTIMATES HAVE WIDE ERROR BARS
CURRENT 2026 COST SCHEDULE APPLIED RETROSPECTIVELY
```

---

## 18. Suspicious-Result Protocol

Do not celebrate unusually strong B001 results.

If the baseline produces results such as:

```text
~30% CAGR
Sharpe ~1.8+
very low drawdown
```

treat the result as suspicious until proven otherwise.

Investigate in this order:

1. corporate-action adjustment;
2. same-day look-ahead;
3. incorrect open/close execution;
4. missing trading costs;
5. cash accounting;
6. position overlap;
7. survivorship effects;
8. missing/delisted symbols;
9. signal shift errors;
10. benchmark alignment.

A boring result is plausible.

A spectacular result requires evidence.

---

## 19. Phase 1 Acceptance Tests

Phase 1 cannot be considered complete until these pass.

### Cost layer

- [ ] Empty day returns zero cost.
- [ ] Flat-price round trip loses exactly costs.
- [ ] Same-symbol same-day sell receives one DP charge under the reference profile.
- [ ] Two sold symbols receive two DP charges.
- [ ] Female-primary DP profile uses the dated discounted DP charge.
- [ ] Stamp duty applies to the correct side.
- [ ] STT half-up rounding is reproduced.
- [ ] Small-trade STT rounding-to-zero behaviour is documented and tested pending real-note validation.
- [ ] STT is aggregated and rounded once per day per side.
- [ ] GST base excludes stamp duty and DP charges.
- [ ] Daily total cost equals the sum of its components.
- [ ] Allocated fill-level costs sum back to the daily authoritative totals.
- [ ] Invalid fills are rejected.
- [ ] Real broker record reconciles when available.

### Data layer

- [ ] NSE UDiFF file loads reproducibly.
- [ ] Raw file remains unchanged.
- [ ] Required schema validated.
- [ ] Monetary OHLC/reference prices are converted to `Decimal` before backtesting.
- [ ] Duplicate rows checked.
- [ ] OHLC integrity checked.
- [ ] Missing-data policy documented.

### Corporate actions

- [ ] Split case tested.
- [ ] Bonus case tested.
- [ ] Unsupported event surfaced.
- [ ] One real event inspected visually.

### Universe

- [ ] Selection rule committed before B001 result.
- [ ] 20-stock list frozen.
- [ ] Freeze date recorded.
- [ ] Survivorship-bias warning present.

### Backtester

- [ ] Signal close(T) cannot execute before open(T+1).
- [ ] Flat-price scenario reconciles.
- [ ] Hand-calculated three-trade sequence matches.
- [ ] Cash never changes without an audited event.
- [ ] Position quantities reconcile.
- [ ] Costs reconcile.
- [ ] Daily NAV invariant holds on every trading day.
- [ ] Any daily NAV invariant breach halts the run.
- [ ] T+1 gap sizing cannot create negative cash.
- [ ] Exit signals always target the full held quantity.
- [ ] Unfillable exits carry forward and retry on the next eligible session.
- [ ] Final NAV reconciles.

### Research

- [ ] B001, B002, and B003 are registered before B001 runs.
- [ ] B001 and B002 are counted as separate trials.
- [ ] B003 hysteresis thresholds are frozen before B001 results are observed.
- [ ] B001 uses the pre-registered weekly rebalance rule.
- [ ] B001 turnover is measured after the run and does not block trades mid-run.
- [ ] Annual turnover pass/fail is reported for each complete calendar year.
- [ ] Turnover FAIL occurs if any complete year exceeds 30; partial first/last years are excluded and not annualised.
- [ ] Strategy max drawdown is compared with benchmark max drawdown over the identical period.
- [ ] Nifty 100 TRI benchmark aligned.
- [ ] Failed results retained.
- [ ] Final report generated.

---

## 20. Phase 1 Exit Criteria

Phase 1 is complete when:

1. one end-to-end B001 backtest runs without unexplained accounting differences;
2. at least one trade is manually reconciled from signal to exit;
3. cost calculations have passed unit tests and real-record validation where available;
4. corporate-action logic has passed a real-event visual check;
5. the frozen universe is version-controlled;
6. strategy and benchmark results are produced net of costs;
7. experiment B001 is permanently recorded;
8. all known limitations are printed in the report;
9. the result can be reproduced from a clean checkout using documented steps;
10. any deviation from frozen Phase 0/1 rules is recorded in `docs/DECISIONS.md`.

Only then may Phase 2 introduce additional strategy research.

---

## 21. Explicit Non-Goals

Do not add during Phase 1:

- broker API integration;
- live trading;
- AI agents;
- LLM decision-making;
- automated parameter search;
- regime detection;
- F&O;
- leverage;
- short selling;
- web dashboard;
- cloud infrastructure;
- distributed workers;
- premature broker abstraction.

---

## 22. Decision Log Rule

Use:

```text
docs/DECISIONS.md
```

for any change to a frozen rule, assumption, cost profile, universe definition, benchmark method, execution convention, or research protocol.

A decision entry should record:

- decision ID;
- date;
- old rule;
- new rule;
- reason;
- affected experiment IDs;
- whether prior results must be rerun.

Do not silently edit a frozen specification after seeing results.

---

## 23. Official References to Re-check


- NSE All Reports / CM-UDiFF Common Bhavcopy Final  
  https://www.nseindia.com/all-reports

- NSE Corporate Filings — Corporate Actions  
  https://www.nseindia.com/companies-listing/corporate-filings-actions

- NSE Indices Historical Data — Total returns Index Values / P-E, P-B & Div Yield values  
  https://www.niftyindices.com/reports/historical-data

- NSE Total Return Index methodology  
  https://www.niftyindices.com/resources/index-concepts/total-return-index

- Zerodha Charges  
  https://zerodha.com/charges/

- Zerodha Exchange Transaction Charges  
  https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/exchange-transaction-charges

- Zerodha DP charges  
  https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/what-do-dp-charges-mean

- Zerodha STT calculation  
  https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/how-is-the-securities-transaction-tax-stt-calculated

---

## 24. First Implementation Task

When Phase 1 coding begins, the first task is:

```text
src/nse_quant/costs/india_equity.py
```

Do not begin B001 until the cost layer and its tests pass.
