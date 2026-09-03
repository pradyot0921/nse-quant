# B004 Research Review V0

**Status:** Rejected before robustness

**Review date:** 2026-09-03

This artifact records the B004 research-period result and gate review. It does
not inspect the validation holdout and does not run B004-S015.

## Boundary

B004 was run only on the pre-registered research period:

```text
2016-01-01 through 2022-12-31
```

The validation holdout remains sealed:

```text
2023-01-01 through 2026-08-19
```

No B004 validation-period strategy NAV, trades, Sharpe, CAGR, drawdown, or
other strategy-performance output was generated.

## Result

| Metric | B004 | Gate | Status |
| --- | ---: | ---: | --- |
| Integrity violations | 0 | 0 | PASS |
| Completed round trips per complete year | max 30 | <= 30 | PASS |
| Maximum drawdown | 0.306676 | <= 0.379228 | PASS |
| CAGR | 0.071975 | >= 0.137013 | FAIL |
| Sharpe | 0.446175 | >= 0.837396 | FAIL |
| Maximum stock positive contribution share | 0.181737 | <= 0.30 | PASS |
| Maximum calendar-year positive contribution share | 0.497509 | <= 0.35 | FAIL |

B004 is rejected because every frozen promotion gate had to pass, and three
gates failed.

## Annual Turnover Detail

| Year | Completed round trips | Gate |
| --- | ---: | --- |
| 2016 | 5 | PASS |
| 2017 | 19 | PASS |
| 2018 | 23 | PASS |
| 2019 | 30 | PASS |
| 2020 | 14 | PASS |
| 2021 | 17 | PASS |
| 2022 | 19 | PASS |

## Regime Exposure

| Metric | Value |
| --- | ---: |
| Risk-on sessions | 1231 |
| Risk-off sessions | 296 |
| Regime unavailable sessions | 199 |
| Risk-on share after SMA available | 0.806156 |
| Risk-off share after SMA available | 0.193844 |
| Weekly regime state changes | 24 |

## Interpretation

B004 did what a broad-market regime overlay would be expected to do in one
important respect: maximum drawdown improved versus both B003 and the Nifty 100
TRI research-period threshold. It also kept every complete-year round-trip
count within the annual turnover limit.

That was not enough. The cost of reduced exposure was too large: CAGR and
Sharpe were both well below the benchmark thresholds. The result also depended
too heavily on one positive calendar year under the pre-registered
calendar-year contribution gate.

The correct conclusion is not to tune the SMA length, threshold, cadence, or
entry/hold rules. Under the Phase 2 specification, B004 failed and must stay
failed.

## B004-S015 Status

B004-S015 is not run.

The robustness row was allowed only if B004 passed every frozen baseline
promotion gate. Because B004 failed, B004-S015 would be a rescue trial and is
therefore prohibited.

## Evidence

| Evidence | Artifact |
| --- | --- |
| B004 report | `experiments/results/B004_research/phase1_report.md` |
| B004 trade log | `experiments/results/B004_research/trade_log.csv` |
| Phase 2 specification | `docs/PHASE_2_RESEARCH_SPEC.md` |
| B004 implementation status | `docs/phase2/B004_IMPLEMENTATION_STATUS_V0.md` |
| Experiment ledger | `experiments/ledger.csv` |

## Next Rule

The next Phase 2 baseline slot may only be used by a new pre-registered
candidate, B005, with a genuinely different externally motivated mechanism.

B005 may not be B004 with a different SMA length, threshold, cadence, position
count, lookback, or slippage assumption.
