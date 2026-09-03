# Phase 1 Research Postmortem V0

**Status:** Research interpretation artifact

**Postmortem date:** 2026-09-03

Phase 1 found no promotable V0 strategy, but it preserved the validation
holdout and produced a reusable, audited research pipeline.

This postmortem interprets the completed Phase 1 research cycle. It does not
revive rejected experiments, does not run robustness rows as rescue trials, and
does not inspect the validation holdout.

## Summary

The Phase 1 engineering objective succeeded. The project can take validated NSE
cash-equity data through corporate-action adjustment, a frozen universe, explicit
T+1 execution, Indian delivery-cost accounting, trade logs, benchmark comparison,
and reproducible reports.

The Phase 1 research objective did not produce a strategy eligible for
promotion. B001, B002, and B003 were all rejected on pre-registered
research-period gates before validation was touched.

This is a useful result. The pipeline now gives an auditable way to say no.

## What Was Tested

All three executed experiments used:

- frozen V0 universe `nifty100_v0_20_d037`;
- frozen adjusted dataset `nifty100_v0_adjusted_ohlcv_d039`;
- research period `2016-01-01..2022-12-31`;
- validation period `2023-01-01..2026-08-19`, left uninspected;
- Nifty 100 TRI benchmark;
- `ZERODHA_NSE_DELIVERY_2026_08` cost profile applied retrospectively;
- baseline adverse deterministic slippage of 0.05%.

The executed candidates were:

| Experiment | Strategy | Turnover Gate | Drawdown Gate | Status |
| --- | --- | --- | --- | --- |
| B001 | 3-position weekly momentum | FAIL | FAIL | REJECTED |
| B002 | 2-position weekly momentum | FAIL | FAIL | REJECTED |
| B003 | 3-position weekly momentum with hysteresis | PASS | FAIL | REJECTED |

B001-S015, B002-S015, and B003-S015 remain unrun robustness rows. They are not
rescue trials.

## What Worked

The trade-level diagnostics were not uniformly bad. B001 showed:

| Metric | Value |
| --- | ---: |
| CAGR | 0.173960 |
| Win rate | 0.485185 |
| Profit factor | 1.376502 |
| Expectancy per completed trade | 274.45 |
| Average winning trade | 2068.07 |
| Average losing trade | -1415.94 |

This matters because the rejection is not simply "the signal never made money."
At the completed-trade level, B001 had positive expectancy and a profit factor
above 1.0. The raw signal had some research-period payoff.

## What Failed

The portfolio-level behavior was unacceptable.

| Experiment | CAGR | Max Drawdown | Benchmark CAGR | Benchmark Max Drawdown | Completed Round Trips |
| --- | ---: | ---: | ---: | ---: | ---: |
| B001 | 0.173960 | 0.466630 | 0.137013 | 0.379228 | 270 |
| B002 | 0.122232 | 0.534276 | 0.137013 | 0.379228 | 199 |
| B003 | 0.136461 | 0.512654 | 0.137013 | 0.379228 | 124 |

B001 had the highest CAGR, but it failed both research gates. Its turnover was
far above the allowed limit, and its maximum drawdown was worse than the Nifty
100 TRI benchmark over the identical research period.

B002 reduced position count from three to two, but it did not solve the problem.
It still failed turnover and had the worst drawdown of the three executed
candidates.

B003 did what it was designed to do on turnover: it reduced completed round
trips and passed the turnover gate. It still failed the benchmark-relative
drawdown gate, so it was rejected.

## Why No Strategy Was Promoted

No strategy was promoted because every executed Phase 1 candidate failed at
least one pre-registered research-period gate before validation.

The central lesson is that concentrated large-cap relative momentum can produce
positive trade-level statistics while still being a poor portfolio candidate.
The combination of two or three positions, weekly rotation, adverse execution,
delivery costs, and benchmark-relative drawdown made the strategy class
unacceptable for promotion.

The correct comparison is not whether the strategy made money in isolation. The
correct comparison is whether it survived the pre-registered research gates
against a Nifty 100 TRI alternative after costs and slippage. It did not.

## Holdout Status

The validation holdout remains sealed:

```text
2023-01-01 through 2026-08-19
```

Do not run B001, B002, B003, B001-S015, B002-S015, or B003-S015 on this period
as a promotion test. The rejected baseline candidates cannot be rescued by
looking at validation results after failing research-period gates.

## Lessons For Next Cycle

The next cycle should not be a tuned variant of the same concentrated momentum
idea. The evidence already says that this V0 strategy family can show positive
trade-level payoff while still concentrating risk too severely.

Useful next-cycle thinking should start from economic reasoning, not parameter
repair. A new hypothesis should explain why its return source is different from
or structurally improves on the rejected V0 premise.

Examples of dimensions that would need fresh reasoning before any test:

- a different economic signal rather than a lookback tweak;
- a risk-control mechanism justified before observing validation data;
- a broader or different universe with a new frozen selection rule;
- a portfolio construction rule that addresses concentration and drawdown before
  results are known;
- a cost or execution assumption change that is justified by external evidence,
  not by desired backtest behavior.

## Next Hypothesis Requirements

Any new strategy, risk overlay, universe change, rebalance rule, cost
assumption, or parameter choice must receive a new experiment ID and be
pre-registered before execution.

A future research cycle should define, before running:

- the economic reason the hypothesis might work;
- the exact universe and data version;
- the research period and untouched validation boundary;
- the entry, exit, sizing, execution, cost, and slippage rules;
- the promotion gates;
- the expected failure modes;
- the reason this is not merely a rescue variant of B001, B002, or B003.

Until a genuinely new candidate passes its own research-period gates, the
validation holdout remains unspent.
