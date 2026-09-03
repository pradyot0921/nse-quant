# B004 Implementation Status V0

**Status:** Stage 2.2 implementation and Stage 2.3 synthetic/unit validation complete

**Date:** 2026-09-03

This artifact records implementation readiness for B004. It is not a B004
research result, does not run B004 on the real research period, and does not
inspect the validation holdout.

## Scope

Implemented:

- 200-session Nifty 100 TRI SMA regime state calculation;
- `RISK_ON` when TRI is greater than SMA200;
- `RISK_OFF` when TRI is less than or equal to SMA200;
- warm-up behavior with regime unavailable before 200 benchmark observations;
- weekly-only regime-filtered hysteresis signals;
- risk-off empty target portfolio, which schedules full exits through the
  existing rebalance loop;
- unfilled risk-off exit carry and retry through existing pending-exit logic;
- regime exposure and weekly state-change reporting;
- stock and calendar-year positive-return concentration metrics;
- direct B004-versus-B003 comparison reporting for CAGR, maximum drawdown,
  Sharpe, turnover, transaction costs, and time invested;
- B004/B004-S015 runner support for research-period execution;
- hard B004/B004-S015 validation-period runner block until a later Phase 3
  promotion artifact exists.

Not implemented in this artifact:

- alternative SMA lengths;
- alternative regime thresholds;
- parameter sweeps;
- B004 real research-period result generation;
- B004-S015 robustness run;
- validation-period strategy execution.

## Synthetic And Unit Validation

The implementation is covered by synthetic/unit tests for:

1. exactly 199 benchmark observations, regime unavailable;
2. exactly 200 benchmark observations, SMA available;
3. `TRI > SMA200`, risk-on;
4. `TRI == SMA200`, risk-off;
5. `TRI < SMA200`, risk-off;
6. risk-off schedules full exits;
7. risk-off creates no entries;
8. unfilled risk-off exit is carried and retried;
9. risk-on delegates to B003 ranking/hysteresis;
10. weekly-only evaluation through precomputed weekly signals;
11. no look-ahead in SMA calculation by using only current and prior benchmark
    observations;
12. ordinary-session-only SMA input through the supplied daily research-session
    series;
13. missing required benchmark observation fails loudly;
14. concentration metrics reproduce hand-calculated fixtures;
15. B004 validation-period runner execution is blocked without a Phase 3
    promotion artifact.

## Boundary

B004 remains `PLANNED` in `experiments/ledger.csv`.

The next permitted step is the first B004 real research-period run:

```text
B004
2016-01-01 through 2022-12-31 only
```

No validation-period strategy output may be generated.

If B004 fails any frozen baseline promotion gate, B004 is rejected and
B004-S015 is not run.

If B004 passes every frozen baseline promotion gate, B004-S015 may run on the
research period only.
