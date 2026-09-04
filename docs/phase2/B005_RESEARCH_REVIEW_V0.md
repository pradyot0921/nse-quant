# B005 Research Review V0

**Status:** Rejected before robustness

**Review date:** 2026-09-04

This artifact records the B005 research-period result and gate review. It does
not inspect the validation holdout and does not run B005-S015.

## Boundary

B005 was run only on the pre-registered research period:

```text
2016-01-01 through 2022-12-31
```

The generated report covers the available ordinary-session research bars:

```text
2016-01-01 through 2022-12-30
```

The validation holdout remains sealed:

```text
2023-01-01 through 2026-08-19
```

No B005 validation-period strategy NAV, trades, Sharpe, CAGR, drawdown, or
other strategy-performance output was generated.

## Result

| Metric | B005 | Gate | Status |
| --- | ---: | ---: | --- |
| Integrity violations | 0 | 0 | PASS |
| Maximum complete-year completed round trips | 51 | <= 30 | FAIL |
| Maximum drawdown | 0.302637 | <= 0.379228 | PASS |
| CAGR | 0.032527 | >= 0.137013 | FAIL |
| Sharpe | 0.332169 | >= 0.837396 | FAIL |
| Maximum stock positive contribution share | 0.263713 | <= 0.30 | PASS |
| Maximum calendar-year positive contribution share | 0.494308 | <= 0.35 | FAIL |

B005 is rejected because every frozen promotion gate had to pass, and four
gates failed.

Before the B005 research run, the runner was corrected to include the
pre-registered direct B005-versus-B003 comparison section in B005 reports. No
B005 research output existed before that report-compliance correction.

## Annual Turnover Detail

| Year | Completed round trips | Gate |
| --- | ---: | --- |
| 2016 | 10 | PASS |
| 2017 | 51 | FAIL |
| 2018 | 47 | FAIL |
| 2019 | 41 | FAIL |
| 2020 | 39 | FAIL |
| 2021 | 38 | FAIL |
| 2022 | 27 | PASS |

## Volatility Exposure

| Metric | Value |
| --- | ---: |
| Realized-volatility lookback sessions | 126 |
| Target volatility | 0.120000 |
| Minimum exposure multiplier | 0 |
| Maximum exposure multiplier | 0.804678 |
| Mean exposure multiplier | 0.478432 |
| Median exposure multiplier | 0.495557 |
| Weekly exposure changes | 339 |
| Zero-exposure session share | 0.073581 |
| Partial-exposure session share | 0.926419 |
| Full-exposure session share | 0.000000 |

## Interpretation

B005 did reduce maximum drawdown versus both B003 and the Nifty 100 TRI
research-period threshold. It also kept stock-level positive P&L concentration
inside the frozen gate.

That was not enough. The volatility overlay cut exposure so much that CAGR and
Sharpe fell far below the benchmark thresholds. It also created frequent
resizing: completed round trips rose to 253, with five complete calendar years
above the annual turnover limit. Positive NAV gains remained too dependent on
one calendar year under the pre-registered calendar-year concentration gate.

This is consistent with the pre-registered cash-constrained adaptation: because
B005 caps exposure at 1.0, the overlay can only reduce exposure below B003, not
increase exposure in calmer periods to offset the return drag.

The correct conclusion is not to tune the volatility target, lookback,
exposure cap, momentum ranks, or slippage assumption. Under the B005
pre-registration, B005 failed and must stay failed.

## B005-S015 Status

B005-S015 is not run.

The robustness row was allowed only if B005 passed every frozen baseline
promotion gate. Because B005 failed, B005-S015 would be a rescue trial and is
therefore prohibited.

## Evidence

| Evidence | Artifact |
| --- | --- |
| B005 report | `experiments/results/B005_research/phase1_report.md` |
| B005 trade log | `experiments/results/B005_research/trade_log.csv` |
| B005 pre-registration | `docs/validation/B005_PREREGISTRATION_V0.md` |
| B005 implementation status | `docs/phase2/B005_IMPLEMENTATION_STATUS_V0.md` |
| Phase 2 specification | `docs/PHASE_2_RESEARCH_SPEC.md` |
| Experiment ledger | `experiments/ledger.csv` |

## Next Rule

The next Phase 2 baseline slot may only be used by a new pre-registered
candidate, B006, with a genuinely different externally motivated mechanism.

B006 may not be B005 with a different volatility target, lookback, exposure
cap, rebalance cadence, position count, momentum ranking rule, or slippage
assumption.
