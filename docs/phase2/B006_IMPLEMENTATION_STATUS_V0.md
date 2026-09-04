# B006 Implementation Status V0

**Status:** B006 implementation ready for input-warm-up data build and research-period review

**Date:** 2026-09-04

This artifact records implementation readiness for B006. It is not a B006
research result, does not build the real B006 input-only warm-up dataset, does
not run B006 on the real research period, and does not inspect the validation
holdout.

## Scope

Implemented:

- weekly 52-week-high proximity ranking signals;
- exact frozen PH52 score:

```text
PH52(i,T) =
adjusted_close(i,T)
/
max(adjusted_close(i,d) for ordinary sessions d where T - 364 calendar days <= d <= T)
```

- inclusive signal-date treatment because decisions are made after the signal
  close and executed no earlier than the next eligible session open;
- complete trailing warm-up enforcement from the performance start date;
- missing adjusted-close rejection inside the required 52-calendar-week window;
- deterministic alphabetical tie-breaking after score sorting;
- unchanged B003-style hysteresis wrapper: entry rank `<=3`, hold rank `<=6`,
  and three maximum positions;
- experiment-layer separation of input-only warm-up bars from research-period
  portfolio NAV;
- B006 and B006-S015 runner support for research-period execution only;
- B006 default processed input path:
  `data/processed/nifty100_v0_52w_high_input_warmup.csv`;
- B006 validation-period runner block until a later Phase 3 promotion artifact
  exists;
- B006 report section for lookback calendar days, frozen window rule, first
  signal date with complete input, missing/invalid PH52 score count, and the
  mandatory 52-week-high limitation warning;
- direct B006-versus-B003 comparison reporting in generated reports.

Not implemented in this artifact:

- alternative high-window lengths;
- threshold or breakout rules;
- volume or moving-average confirmations;
- B003 momentum combination;
- B004 trend-filter combination;
- B005 volatility-scaling combination;
- parameter sweeps;
- the real B006 input-only warm-up processed dataset;
- B006 real research-period result generation;
- B006-S015 robustness run;
- validation-period strategy execution.

## Synthetic And Unit Validation

The implementation is covered by synthetic/unit tests for:

1. PH52 ranking from current adjusted close divided by trailing-window adjusted
   high;
2. inclusive signal-date behavior;
3. alphabetical tie-breaking;
4. B006 hysteresis holding until the hold-rank threshold breaks;
5. incomplete required warm-up rejection;
6. missing symbol/date adjusted-close rejection inside the required window;
7. first complete-input signal-date reporting;
8. experiment wiring that uses warm-up bars for signals but starts performance
   NAV only at the research-period start;
9. B006 report metadata and mandatory limitation warning;
10. B006 script support for research-only synthetic execution with warm-up
    input;
11. B006 validation-period runner execution blocked without a Phase 3 promotion
    artifact.

## Boundary

B006 and B006-S015 remain `PLANNED` in `experiments/ledger.csv`.

The next permitted step, after review and merge, is the B006 input-only warm-up
dataset construction:

```text
Build sufficient pre-2016 adjusted OHLCV input history to compute PH52 on the
first eligible 2016 signal date.
```

That data build must produce the pre-registered artifact:

```text
docs/validation/B006_INPUT_WARMUP_DATASET_V0.md
```

If the warm-up dataset cannot be built cleanly under deterministic V0 data and
corporate-action rules, B006 must be cancelled before real research execution.

No validation-period strategy output may be generated.

If the warm-up dataset is built cleanly, the next permitted run is:

```text
B006
2016-01-01 through 2022-12-31 only
```

If B006 fails any frozen baseline promotion gate, B006 is rejected and
B006-S015 is not run.

If B006 passes every frozen baseline promotion gate, B006-S015 may run on the
research period only.
