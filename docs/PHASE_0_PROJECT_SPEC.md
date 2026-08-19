# Phase 0 — Project Specification and Research Rules

**Project:** NSE Quant Research and Trading System  
**Phase:** 0  
**Status:** FROZEN  
**Primary market:** NSE cash equity, delivery segment  
**Research style:** Long/cash, swing/position trading  
**Starting simulated capital:** ₹50,000  
**Last updated:** 19 August 2026

---

## 1. Purpose

The purpose of this project is to build a small, auditable quantitative research and trading system for Indian cash equities.

The immediate goal is **not** to build an autonomous AI trader and **not** to guarantee profit.

The goal is to create a system that can:

1. obtain and validate market data;
2. model Indian transaction costs accurately;
3. generate deterministic trading signals;
4. backtest those signals without look-ahead bias;
5. compare performance with an appropriate passive benchmark;
6. record every experiment, including failures;
7. reject strategies that do not survive costs and validation;
8. simulate execution and reconcile cash, holdings, and P&L;
9. later support controlled broker integration only after the research pipeline is trustworthy.

Profit is an outcome to be investigated, not an assumption built into the design.

---

## 2. Core Design Principle

The trading path must be deterministic, testable, and auditable.

### Trading path

```text
Market Data
    ↓
Data Validation
    ↓
Corporate-Action Adjustment
    ↓
Strategy Signal
    ↓
Portfolio / Position Logic
    ↓
Cost + Execution Model
    ↓
Simulated Order / Fill
    ↓
Cash + Holdings Reconciliation
    ↓
Performance + Benchmark Report
```

### AI / LLM role

LLMs are not part of the trading path in V0 or V1.

Future permitted roles may include:

- research-assistant work;
- summarising papers and strategy hypotheses;
- reviewing experiment results;
- generating post-trade explanations;
- helping write documentation.

LLMs must not:

- calculate statutory trading charges used for settlement;
- perform risk checks;
- approve compliance;
- calculate portfolio state;
- directly send broker orders;
- override deterministic controls.

Complexity must earn its existence.

---

## 3. Locked Market Scope

### 3.1 Market

- Exchange focus: NSE
- Segment: cash equity
- Trade type: delivery
- Direction: long or cash
- Overnight cash-equity shorting: not permitted in this project
- Intraday strategies: out of scope
- F&O: out of scope
- Currency derivatives: out of scope
- Crypto trading: out of scope

Crypto data may be used only as a disposable software-development sandbox for testing generic engine behaviour. Strategy conclusions must be produced using NSE data.

### 3.2 Trading horizon

The project is intended for swing / position-style trading.

The original 3–15-session forced holding constraint is **not** imposed on the first momentum baseline.

For B001:

- entries and exits are determined by the strategy rule;
- the annual turnover ceiling remains the control on excessive trading;
- future strategies may define their own minimum or maximum holding periods if economically justified.

### 3.3 Turnover

- Maximum accepted research turnover: **30 completed round trips per calendar year** for the initial strategy class.
- This is a ceiling, not a target.
- A strategy producing 8 or 15 high-quality trades is not penalised for failing to reach 30.
- The backtest engine **must not block the 31st trade or alter strategy behaviour because of this ceiling**.
- Turnover is measured after the run and used as an acceptance/rejection criterion.
- **Aggregation rule:** the specification fails the turnover gate if **any complete calendar year** exceeds 30 completed round trips.
- A strategy does not pass merely because its median or average annual turnover is ≤30.
- Partial calendar years at the beginning or end of the test are reported separately and **excluded from turnover PASS/FAIL**.
- Partial years must not be annualised for the turnover gate.
- A failing specification may be followed only by a separately pre-registered experiment; the original run is never retroactively modified.

---

## 4. Capital and Portfolio Assumptions

### 4.1 Starting capital

Initial simulated capital:

**₹50,000**

Live trading is explicitly excluded from Phase 0 and Phase 1.

### 4.2 Position count

Position count is **not permanently fixed at three**.

The cost model must compare at least:

- 2 concurrent positions, approximately ₹25,000 each;
- 3 concurrent positions, approximately ₹16,667 each.

The choice will be evidence-based because fixed DP charges make smaller position sizes relatively more expensive.

### 4.3 Capital scaling

Possible future research levels:

- ₹50,000 initial simulated capital;
- ₹2–3 lakh only after evidence supports scaling;
- 6–8 positions may be considered only after capital is materially larger and the strategy has passed the promotion process.

No capital increase is automatic.

---

## 5. Risk Constitution

Risk controls are part of the project constitution even though Phase 0 and Phase 1 are simulation-only.

### 5.1 Exposure

For V0/V1:

- no leverage;
- no margin-funded positions;
- long/cash only;
- gross portfolio exposure must not exceed 100% of NAV;
- whole-share quantities only;
- the 2-position specification targets no more than approximately 50% of NAV per position at entry/rebalance;
- the 3-position specification targets no more than approximately 33.34% of NAV per position at entry/rebalance.

Price movement may cause an existing position to drift above its original target weight. That drift is reported rather than forcibly rebalanced unless the strategy rule requires a rebalance.

### 5.2 B001 stop-loss policy

B001 deliberately has **no price-based stop-loss**.

This is intentional: B001 is meant to test a clean ranking-based momentum rule without mixing in an additional stop parameter.

The absence of a stop in B001 must not be interpreted as permission for future live systems to operate without risk controls.

### 5.3 Drawdown policy

Backtests must run through the full historical period and must **not** terminate early because of a research drawdown threshold. Stopping the historical path would distort measurement.

#### Research drawdown gate

For backtest and research promotion:

- maximum drawdown is measured on daily strategy NAV;
- benchmark maximum drawdown is measured over the **identical evaluation period** using the aligned Nifty 100 TRI series;
- a candidate fails the minimum drawdown gate if its maximum drawdown is **worse than the benchmark's maximum drawdown over the same period**;
- a candidate with a lower maximum drawdown than the benchmark passes the minimum drawdown gate, but promotion still depends on return, risk-adjusted performance, turnover, costs, and validation;
- drawdown improvement must be reported in percentage points and relative to benchmark drawdown;
- no extra arbitrary absolute research drawdown threshold is imposed in V0/V1;
- research drawdown is an evaluation gate, not an in-engine trade blocker.

#### Future live-account drawdown limit

Live deployment serves a different purpose and therefore uses an absolute tolerance.

The constitutional live-account limit is:

```text
MAXIMUM LIVE ACCOUNT DRAWDOWN FROM HIGH-WATER MARK: 15%
```

At or beyond that limit:

```text
STOP NEW ENTRIES
HALT AUTOMATED TRADING
REQUIRE HUMAN REVIEW BEFORE RESTART
```

The 15% live-account limit is not used to judge historical strategy quality.

Other live controls, including a daily-loss limit, must still be defined before any live-capital phase.

### 5.4 Deterministic kill switches

A research run or paper-execution process must halt immediately on an accounting or state-integrity failure, including:

- daily NAV invariant breach;
- negative cash beyond documented rounding tolerance;
- missing valuation for a currently held security;
- unsupported/ambiguous corporate action affecting a held security;
- duplicated order/fill identifier;
- impossible position quantity;
- local position state differing from broker state once broker integration exists.

These are operational kill switches. They are not discretionary strategy exits.

### 5.5 Live-trading prohibition

Phase 0 and Phase 1 contain no live brokerage execution.

No live-capital deployment may occur until a later phase defines and approves:

- maximum live account drawdown;
- maximum daily loss;
- maximum order rate;
- stale-data policy;
- broker reconciliation policy;
- emergency flatten/pause procedure;
- human approval and restart procedure.

---

## 6. Starting Universe

### 6.1 Broader research universe

Long-term intended universe:

**Nifty 100**

### 6.2 V0 fixed universe

For the first vertical slice, use a fixed list of **20 liquid large-cap stocks** with sufficiently continuous daily trading history.

The V0 universe is intentionally allowed to contain survivorship bias.

That compromise is accepted to get the pipeline working.

### 6.3 Mandatory dataset label

Every report using the V0 universe must carry:

```text
RESEARCH DATASET V0
SURVIVORSHIP-BIASED: YES
POINT-IN-TIME UNIVERSE: NO
PRODUCTION RESEARCH: NO
```

### 6.4 Universe freezing rule

Before running B001:

1. Write the selection criteria into the repository.
2. Generate the resulting 20-symbol list.
3. Store the list in a version-controlled file.
4. Record the freeze date.
5. Commit it.
6. Do not replace symbols after seeing strategy results.

Changing the universe after seeing results is a new experiment and must receive a new experiment ID.

### 6.5 Initial mechanical selection criteria

The V0 list should be selected mechanically from eligible large-cap names using rules such as:

- Nifty 100 membership at the chosen freeze date;
- EQ series where applicable;
- sufficiently continuous trading history back toward the chosen research start date;
- high median daily traded value;
- no severe unresolved data-quality issue.

The exact thresholds must be written before the resulting list is generated.

---

## 7. Data Scope

### 7.1 Primary source

Primary raw daily-market source:

**NSE CM-UDiFF Common Bhavcopy Final**

NSE discontinued the older CM bhavcopy/common-bhavcopy formats in July 2024 and directs users to the UDiFF common bhavcopy format.

### 7.2 Raw-data rule

Downloaded raw files must be stored unchanged.

```text
data/
├── raw/
└── processed/
```

Never overwrite the original raw file with cleaned or adjusted data.

### 7.3 Required fields

At minimum, the research dataset needs:

- trading date;
- symbol / security identifier;
- series;
- open;
- high;
- low;
- close;
- traded volume;
- traded value / turnover if available;
- other fields required to validate liquidity and data quality.

### 7.4 Numeric representation

All monetary price fields used by accounting, execution, or NAV calculations must be converted to `Decimal` during ingestion/normalisation.

Do not carry binary floating-point prices into the backtester.

At minimum convert:

- open;
- high;
- low;
- close;
- any execution/reference price used by the simulator.

Volumes and integer counts may remain integer types.

This keeps accounting invariants meaningful and prevents tolerance from being loosened merely to accommodate floating-point noise.

### 7.5 Data-quality checks

At minimum:

- duplicate symbol/date rows;
- missing dates;
- impossible OHLC relationships;
- zero/negative prices;
- suspicious extreme returns;
- series changes;
- symbol changes;
- missing corporate-action records where expected;
- non-trading days handled correctly.

---

## 8. Corporate Actions

Corporate-action adjustment is a first-class module, not a helper buried inside the loader.

Initial mandatory coverage:

- stock splits;
- bonus issues.

Later coverage may include:

- consolidations;
- rights;
- mergers / demergers;
- symbol changes;
- other reorganisations.

Dividend handling depends on the specific strategy and benchmark methodology and must be documented separately.

### 8.1 Source

NSE publishes corporate actions separately, including symbol, purpose, ex-date, record date, and related information.

### 8.2 Adjustment module

Target module:

```text
src/nse_quant/data/corporate_actions.py
```

Responsibilities:

1. ingest corporate-action data;
2. normalise the event description;
3. identify supported actions;
4. calculate adjustment factors;
5. join events to the relevant security by symbol/security identifier and ex-date;
6. generate adjusted price history;
7. expose warnings for unsupported or ambiguous events;
8. never silently guess an adjustment factor.

### 8.3 Mandatory validation

Before using adjusted data downstream:

- choose at least one known stock with a split or bonus in the research period;
- inspect the raw series around the ex-date;
- inspect the adjusted series;
- verify the discontinuity disappears as expected;
- inspect a chart manually;
- add a unit/integration test for the event.

If adjustment cannot be trusted, downstream strategy results are invalid.

---

## 9. Benchmark

Primary benchmark:

**Nifty 100 Total Return Index (TRI)**

Primary historical source:

**NSE Indices Historical Data → Total returns Index Values → Nifty 100**

Use the TRI rather than the price-only index because the TRI includes dividend effects and reinvestment.

If the TRI series cannot be retrieved for an engineering run, a fallback may be constructed from the Nifty 100 price-index series plus a separately sourced historical dividend-yield estimate from NSE Indices. That fallback must be labelled:

```text
BENCHMARK: APPROXIMATE NIFTY 100 TOTAL-RETURN PROXY
OFFICIAL TRI SERIES: UNAVAILABLE FOR THIS RUN
USE FOR STRATEGY PROMOTION: NO
```

The approximate fallback is permitted only to keep the software pipeline moving. It is not acceptable evidence for strategy promotion.

Strategy success is not measured only by rupee profit.

Compare at least:

- CAGR;
- annualised volatility;
- maximum drawdown;
- Sharpe ratio;
- Sortino ratio;
- Calmar ratio;
- turnover;
- exposure / time in market;
- net return after trading costs;
- worst periods / tail behaviour.

A complex strategy that does not outperform an appropriate passive benchmark on a sufficiently convincing risk-adjusted basis should not be promoted.

---

## 10. Execution Convention

The execution convention must prevent look-ahead bias.

### 10.1 Signal timing

```text
Signal calculation:
After market close on trading day T

Earliest assumed execution:
Trading day T+1

Initial execution price assumption:
T+1 open
```

### 10.2 Exit timing

If an exit condition is calculated using day T closing information:

```text
Exit signal:
After close on T

Execution:
T+1 open
```

Never calculate a signal with day T closing data and pretend the trade executed at the same day T close.

### 10.3 Explicit event loop

The initial backtester should use an explicit trading-day loop.

Avoid a heavily vectorised design until portfolio accounting and execution timing are independently verified.

Correctness is more important than speed in V0.

---

## 11. Trading-Cost Policy

Trading costs must be modelled before evaluating strategies.

Do not use a single constant such as:

```python
cost = 0.0035
```

The cost model must calculate components independently.

### 11.1 Cost categories

At minimum:

- brokerage;
- securities transaction tax (STT);
- exchange transaction charges;
- SEBI turnover charges;
- GST where applicable;
- stamp duty;
- DP charges;
- slippage.

Slippage belongs to the execution/fill model, not the statutory-fee module.

### 11.2 Broker-specific profiles

Broker-specific charges must be named and dated.

Example:

```text
ZERODHA_NSE_DELIVERY_2026_08
```

Do not assume this profile applies to every broker.

### 11.3 Current Zerodha reference profile

For implementation testing only, the current Zerodha resident-individual NSE equity-delivery schedule checked on 19 August 2026 includes:

- delivery brokerage: ₹0;
- STT: 0.1% on buy and sell;
- NSE cash transaction charge: 0.00307%;
- SEBI charge: ₹10 per crore;
- GST: 18% on brokerage + SEBI charges + transaction charges;
- stamp duty on equity delivery: **0.015% on the buy side** under the currently published Zerodha schedule;
- DP pre-GST base for a male primary holder: ₹13 per sold stock per day;
- DP pre-GST base for a female primary holder: ₹12.75 per sold stock per day.

These values are **dated reference assumptions**, not permanent constants.

### 11.3.1 Rounding policy

Where a charge must be rounded to the nearest rupee, the implementation must use explicit commercial half-up rounding:

```python
Decimal.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
```

Do not rely on `Decimal.quantize()` defaults. Python's default rounding mode may produce banker's rounding (`ROUND_HALF_EVEN`), which would incorrectly round a value such as ₹10.50 to ₹10 instead of ₹11 for a half-up rule.

The exact rounding point used by the selected broker/exchange must be validated against real records.

### 11.3.2 Historical-cost assumption

For the initial historical backtests, the project intentionally applies the **current 2026 reference fee schedule to older market data**.

This is a counterfactual economic question:

> How would this historical strategy have performed under approximately today's transaction-cost structure?

It is **not** a reconstruction of the historical fee regime. STT and other charges have changed over time.

Every report using this assumption must label it clearly, for example:

```text
COST MODEL: CURRENT 2026 REFERENCE SCHEDULE APPLIED RETROSPECTIVELY
HISTORICAL FEE RECONSTRUCTION: NO
```

If the project later needs historically accurate realised-cost simulation, dated fee schedules must be implemented separately.

Re-check broker and statutory charges before live trading.

### 11.4 STT daily aggregation

For the V0 Zerodha reference implementation, delivery STT is calculated from **daily per-side turnover**:

1. sum all delivery BUY turnover for the trading day;
2. apply the delivery STT rate;
3. round that buy-side STT once using the specified half-up rule;
4. separately sum all delivery SELL turnover for the day;
5. apply the delivery STT rate;
6. round that sell-side STT once using the specified half-up rule.

Do not round STT independently on every fill and then sum the rounded fill values.

This aggregation rule must be checked against an actual contract note. If the selected broker's documented settlement convention differs, the named broker profile must encode that difference.

### 11.5 Fill-level reporting allocation

Daily cost totals are the authoritative accounting values.

Fill-level and symbol-level cost figures used in logs, reports, and manual reconciliation are reporting allocations only. They must be labelled as allocations, and they must sum back exactly to the daily authoritative component totals.

Initial allocation rule:

- DP charges are assigned directly to sold symbols.
- If one sold symbol has multiple same-day sell fills, its DP charge is allocated across those fills pro-rata by that symbol's same-day sell turnover.
- Buy-side STT and stamp duty are allocated across buy fills pro-rata by buy turnover.
- Sell-side STT is allocated across sell fills pro-rata by sell turnover.
- Brokerage, exchange transaction charges, SEBI charges, and GST are allocated across all fills pro-rata by turnover.

Do not use allocated fill-level charges to override the daily authoritative accounting total.

### 11.6 DP-charge aggregation

For the reference Zerodha model:

- selling one stock multiple times on the same day produces one DP charge for that stock under a normal single-settlement case;
- selling multiple distinct stocks on the same day aggregates the pre-GST DP base across all distinct sold stocks, then applies GST once to that aggregate;
- DP charges are not treated as a per-fill percentage;
- exceptional separate-settlement cases must be modelled explicitly if they become relevant.

### 11.7 GST-base protection

For the current Zerodha reference profile, GST is applied to:

```text
brokerage + SEBI charges + exchange transaction charges
```

The GST base must **exclude stamp duty and DP charges**.

DP GST is included inside the DP charge total after aggregating the pre-GST DP base. It must not be included in the normal trading-charge GST component and must not be taxed a second time.

### 11.8 Slippage direction

Slippage must be adverse in the initial deterministic model:

```text
BUY fill  = reference price × (1 + slippage_rate)
SELL fill = reference price × (1 - slippage_rate)
```

where `slippage_rate >= 0`.

Do not use symmetric random slippage that averages to zero in V0/V1.

Initial frozen assumptions:

```text
Baseline adverse deterministic slippage:   0.05%
Robustness adverse deterministic slippage: 0.15%
```

The 0.15% robustness assumption is a separate pre-registered parameter specification and must not be chosen after seeing baseline results.

### 11.9 Cost vs income tax

Trading costs and personal income tax must remain separate.

The backtester reports:

```text
Gross strategy P&L
- transaction costs
- slippage
= net trading P&L
```

Any estimated taxpayer-specific income-tax treatment belongs in a separate analysis layer and must not be hard-coded into the trading engine.

### 11.10 Real-record reconciliation standard

When validating the cost engine against an actual broker contract note and related funds/depository entries:

```text
Acceptance criterion:
absolute difference in daily total charges ≤ ₹1
```

Do not require paise-perfect agreement for every individual component because brokers and exchanges may round or aggregate at different intermediate stages.

Any daily-total difference greater than ₹1 must be investigated and explained before the cost model is accepted.

---

## 12. Research Discipline

The research system must be designed to avoid industrialised overfitting.

### 12.1 Experiment ledger

Every attempted hypothesis or parameter specification receives an experiment ID.

Example:

```text
B001
B002
B003
...
```

The ledger must retain failures.

Do not delete failed experiments.

### 12.2 What counts as a trial

Every parameter change counts as an additional trial.

For example, testing lookbacks of:

```text
40, 60, 80, 100, 120 days
```

is multiple specifications, not one magical “momentum test.”

### 12.3 Pre-registration

Before running an experiment, record:

- experiment ID;
- hypothesis;
- economic rationale;
- universe version;
- date range;
- signal definition;
- entry rule;
- exit rule;
- position-sizing rule;
- turnover limit;
- parameters to be tested;
- evaluation metrics.

### 12.4 Validation policy

As the project matures, research validation may use:

- train / validation / test separation;
- walk-forward analysis;
- purged validation where appropriate;
- combinatorial purged cross-validation where appropriate;
- parameter-sensitivity analysis;
- Deflated Sharpe Ratio;
- White's Reality Check;
- Hansen's SPA or related multiple-testing methods.

The key principle is that repeatedly selecting winners on the same “out-of-sample” data contaminates that data.

### 12.5 Holdout policy

A holdout block loses its status as unseen data once inspected.

Newly accumulated market data can become the next genuinely unseen evaluation frontier.

Never describe repeatedly inspected data as untouched out-of-sample evidence.

---

## 13. Baseline Strategy B001

B001 exists to validate the pipeline, not to prove a profitable edge.

Initial family:

**cross-sectional / relative momentum baseline**

The first three experiment specifications are pre-registered before any result is observed.

### B001 — 3-position weekly momentum baseline

- signal: 60-session prior return;
- rank the frozen universe;
- hold the top 3 eligible names;
- long/cash only;
- no arbitrary 15-session forced exit;
- evaluate the ranking once per week at the close of the final NSE trading session of that week;
- schedule resulting changes for the next NSE trading session's open;
- exit a holding at the weekly rebalance if it is no longer in the top 3 or becomes ineligible;
- measure the 30-round-trip annual turnover ceiling after the run; do not block trades mid-run.

### B002 — 2-position cost/concentration variant

B002 uses the same signal, weekly rebalance schedule, execution convention, and exit logic as B001 but holds the top 2 eligible names.

B002 is a separate trial because fixed DP charges interact materially with position size at ₹50,000 capital.

### B003 — Pre-registered hysteresis response

B003 is registered **before B001 is run** as the planned response if B001 exceeds the turnover mandate.

```text
Signal: 60-session prior return
Entry threshold: rank 3 or better
Hold while: rank 6 or better
Exit threshold: below rank 6, or ineligible
Rebalance observation: weekly
Execution: next NSE trading session open
Maximum positions: 3
Direction: long/cash
```

B003 remains in the experiment ledger even if B001 passes the turnover gate and B003 is never needed.

If B001 exceeds 30 completed round trips in any complete calendar year, mark B001 as a turnover failure and then run the already-registered B003. Do not invent a new hysteresis threshold after seeing B001's result.

Do not optimise many lookback values, rebalance schedules, ranking thresholds, stops, or hysteresis bands before these frozen baselines are evaluated.

A boring or underperforming B001 result is acceptable.

A suspiciously spectacular result is a reason to search for a bug.

---

## 14. Mandatory Sanity Tests

Before trusting strategy results:

### Test A — Flat-price accounting

A flat price series must produce:

```text
ending capital = starting capital - applicable costs
```

No strategy alpha can appear from a flat series.

### Test B — Hand-calculated trade sequence

A manually constructed three-trade sequence must match the engine:

- fills;
- cash;
- quantities;
- costs;
- holdings;
- realised P&L;
- unrealised P&L;
- final NAV.

Match to the rupee, and ideally to the paise where the broker/exchange calculation permits.

### Test C — Corporate action

A known split/bonus case must show:

- broken/raw price discontinuity;
- correctly adjusted historical series;
- expected return continuity.

### Test D — Timing

A signal generated using close(T) must not execute before open(T+1).

### Test E — Daily NAV invariant

All prices entering the backtester are `Decimal`, so the invariant is checked using exact Decimal arithmetic at the project's documented money precision:

```text
NAV == cash + Σ(quantity × official close for every holding)
```

After each trading day's fills and mark-to-market step:

- quantize monetary values consistently to the documented accounting precision;
- compare the resulting `Decimal` values directly;
- do **not** introduce a widening floating-point tolerance during debugging.

A breach halts the run immediately. Final-NAV reconciliation alone is insufficient because an intermediate error can corrupt drawdown and other path-dependent metrics even if it later cancels out.

If a held security has no valid valuation price for the day, V0 must halt rather than silently forward-fill.

### Test F — Gap-aware entry sizing and exit semantics

A signal generated at close(T) creates an **entry order intent**, not a guaranteed entry quantity.

At open(T+1), for entries:

1. apply adverse slippage to the reference open;
2. process scheduled exits before new entries;
3. determine available cash;
4. recompute the affordable whole-share entry quantity using the actual simulated fill price and applicable buy charges;
5. round quantity down;
6. if the intended quantity is unaffordable, reduce it;
7. if even one share is unaffordable, skip the entry;
8. log every resize or skip.

For exits:

- an exit order is always for the **full currently held quantity**;
- do not resize an exit because the open price changed;
- do not intentionally leave a stub position.

If an exit cannot fill at all because there is no executable trade at the modeled open, including a circuit/no-trade condition:

```text
EXIT_UNFILLED
CARRY_POSITION_FORWARD
RETRY_NEXT_ELIGIBLE_SESSION
```

The full position remains in holdings, continues to be marked to market when a valid close exists, and the pending exit is retried on the next trading session where the execution model permits a fill.

If there is also no valid close for valuation while the position is held, the existing missing-valuation kill switch applies.

The engine must never allow a gap-up entry to create unintended negative cash and must never silently convert a full exit into a partial/stub exit.

---

## 15. What Is Out of Scope for Phase 0–1

Do not build yet:

- multi-agent architecture;
- LLM trading agent;
- machine-learning price prediction;
- regime classifier;
- dynamic AI strategy weighting;
- live brokerage integration;
- broker abstraction layer;
- microservices;
- cloud deployment;
- dashboard;
- database server;
- options/futures;
- leverage;
- high-frequency trading;
- automated strategy generation;
- autonomous parameter search.

---

## 16. Promotion Philosophy

Future strategy lifecycle:

```text
Hypothesis
    ↓
Pre-registered Experiment
    ↓
Research Backtest
    ↓
Validation
    ↓
Multiple-testing Adjustment
    ↓
Frozen Candidate
    ↓
Paper / Forward Test
    ↓
Shadow Live
    ↓
Small-Capital Live
    ↓
Evidence-Based Scaling
```

No strategy may skip levels.

No research component may directly promote itself into live execution.

---

## 17. Phase 0 Exit Criteria

Phase 0 is complete when all of the following are frozen:

- [ ] Market scope is accepted.
- [ ] Starting capital assumption is accepted.
- [ ] Long/cash constraint is accepted.
- [ ] Turnover post-run acceptance rule is accepted.
- [ ] Risk constitution is accepted.
- [ ] Starting universe-selection rule is written.
- [ ] Benchmark is fixed.
- [ ] Execution timing convention is fixed.
- [ ] Cost-model architecture is fixed.
- [ ] Corporate-action requirements are fixed.
- [ ] Research/experiment rules are fixed.
- [ ] V0 non-goals are fixed.
- [ ] B001/B002/B003 pre-registration is accepted.
- [ ] Decimal-at-ingestion rule is accepted.
- [ ] Repository naming and initial structure are agreed.
- [ ] `docs/DECISIONS.md` exists and is used for changes to frozen decisions.

Any future change to a frozen Phase 0 decision must be recorded in a decision log.

---

## 18. Official References to Re-check

These references are included for implementation verification and should be re-checked before live use.

- NSE All Reports / CM-UDiFF Common Bhavcopy Final  
  https://www.nseindia.com/all-reports

- NSE Corporate Filings — Corporate Actions  
  https://www.nseindia.com/companies-listing/corporate-filings-actions

- NSE Indices Historical Data — includes Total returns Index Values and historical dividend-yield data  
  https://www.niftyindices.com/reports/historical-data

- NSE Total Returns Index methodology  
  https://www.niftyindices.com/resources/index-concepts/total-return-index

- Zerodha Charges  
  https://zerodha.com/charges/

- Zerodha Exchange Transaction Charges  
  https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/exchange-transaction-charges

- Zerodha DP-charge explanation  
  https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/what-do-dp-charges-mean

- Zerodha STT explanation  
  https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/how-is-the-securities-transaction-tax-stt-calculated

---

## 19. Specification Governance

Use this file as the project constitution regardless of which editor, coding assistant, IDE, or workspace is used.

When implementation work creates a conflict with this document:

1. do not silently change behaviour;
2. identify the conflict;
3. decide whether the code or specification should change;
4. record the decision;
5. update this file only when the project decision has genuinely changed.
