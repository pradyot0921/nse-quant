# B005 Implementation Status V0

**Status:** B005 implementation ready for research-period review

**Date:** 2026-09-04

This artifact records implementation readiness for B005. It is not a B005
research result, does not run B005 on the real research period, and does not
inspect the validation holdout.

## Scope

Implemented:

- target-exposure support in rebalance planning without changing the default
  full-investment behavior used by prior experiments;
- target-exposure sizing that can reduce overweight holdings, buy underweight
  desired holdings, and suppress buys while required sell-downs are pending;
- rebalance-loop support for applying B005 exposure multipliers on the next
  eligible session open;
- carry and retry of unfilled target-exposure reductions;
- B005 weekly volatility-scaled hysteresis momentum signals using the frozen
  B003 ranking and hysteresis rules;
- 126 ordinary-session realized-volatility lookback;
- 12% annualized target volatility;
- long/cash no-leverage cap at 100% exposure;
- warm-up, missing, zero, or non-positive realized-volatility behavior that
  moves to cash exposure;
- B005 exposure summary reporting with min, max, mean, median, weekly exposure
  changes, and zero, partial, and full exposure session shares;
- mandatory B005 realized-volatility limitation warning in generated reports;
- B005 and B005-S015 runner support for research-period execution;
- hard B005 and B005-S015 validation-period runner block until a later Phase 3
  promotion artifact exists.

Not implemented in this artifact:

- alternative volatility lookbacks;
- alternative volatility targets;
- leverage;
- parameter sweeps;
- B005 real research-period result generation;
- B005-S015 robustness run;
- validation-period strategy execution.

## Synthetic And Unit Validation

The implementation is covered by synthetic/unit tests for:

1. optional target exposure carrying through rebalance plans without forcing
   order resizes;
2. invalid target exposure rejection;
3. target exposure reducing overweight holdings and buying underweight desired
   holdings;
4. buy suppression while a required target-exposure sell-down is pending;
5. next-session-open execution of target-exposure rebalance orders;
6. retry of blocked target-exposure reductions;
7. warm-up cash exposure until enough reference return observations exist;
8. realized-volatility calculation from prior squared daily reference returns;
9. exposure multiplier cap at 1.0;
10. volatility exposure summary session counts, shares, and weekly changes;
11. B005 experiment wiring from reference B003 NAV to volatility-scaled target
    exposure;
12. B005 report exposure statistics and mandatory limitation warning;
13. B005 script support for research-only synthetic execution;
14. B005 validation-period runner execution blocked without a Phase 3 promotion
    artifact.

## Boundary

B005 and B005-S015 remain `PLANNED` in `experiments/ledger.csv`.

The next permitted step, after review and merge, is the first B005 real
research-period run:

```text
B005
2016-01-01 through 2022-12-31 only
```

No validation-period strategy output may be generated.

If B005 fails any frozen baseline promotion gate, B005 is rejected and
B005-S015 is not run.

If B005 passes every frozen baseline promotion gate, B005-S015 may run on the
research period only.
