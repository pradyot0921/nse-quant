# Phase 1 Research-Stage Review V0

**Status:** Evidence artifact

This review summarizes the Phase 1 research-period strategy runs completed
before inspecting the validation holdout. The validation period
`2023-01-01..2026-08-19` remains uninspected for B001, B002, and B003.

## Inputs

| Field | Value |
| --- | --- |
| Research period | `2016-01-01..2022-12-31` |
| Observed report period | `2016-01-01..2022-12-30` |
| Validation period | `2023-01-01..2026-08-19` |
| Universe version | `nifty100_v0_20_d037` |
| Dataset version | `nifty100_v0_adjusted_ohlcv_d039` |
| Benchmark | `Nifty 100 TRI` |
| Starting capital | `50000.00` |
| Cost profile | `ZERODHA_NSE_DELIVERY_2026_08` |

The observed report period ends on `2022-12-30` because that is the final NSE
research-bar session before the pre-registered research-period end date.

## Results

| Experiment | Strategy | CAGR | Max Drawdown | Benchmark CAGR | Benchmark Max Drawdown | Completed Round Trips | Turnover Gate | Drawdown Gate | Status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| B001 | 3-position weekly momentum | 0.173960 | 0.466630 | 0.137013 | 0.379228 | 270 | FAIL | FAIL | REJECTED |
| B002 | 2-position weekly momentum | 0.122232 | 0.534276 | 0.137013 | 0.379228 | 199 | FAIL | FAIL | REJECTED |
| B003 | 3-position weekly momentum with hysteresis | 0.136461 | 0.512654 | 0.137013 | 0.379228 | 124 | PASS | FAIL | REJECTED |

## Interpretation

B001 produced the highest research-period CAGR but failed both gates. Its 270
completed round trips violated the pre-registered turnover mandate, and its
maximum drawdown was worse than the benchmark.

B002 reduced completed round trips versus B001, but still failed the turnover
gate and also failed the benchmark-relative drawdown gate.

B003 was the pre-registered response to B001's excessive turnover. It reduced
completed round trips from 270 to 124 and passed the turnover gate, but failed
the benchmark-relative drawdown gate.

No Phase 1 strategy run qualifies for validation-period inspection.

## Holdout Status

The validation holdout has not been spent on B001, B002, or B003. Because all
three research-period candidates were rejected before validation, the project
must not run validation for these rejected configurations as if it were still a
promotion test.

## Unrun Robustness Rows

B001-S015, B002-S015, and B003-S015 remain unrun in the ledger. They are
higher-slippage robustness rows, not rescue trials. Running them after the
baseline research candidates have already failed would not create a validation
candidate under the current Phase 1 protocol.

## Next Step

Stop Phase 1 strategy execution and review the research design. Any new
strategy, threshold, universe change, cost assumption, or risk gate must be
pre-registered as a new experiment before any validation data is inspected.
