# V0 Universe Selection Rule

**Status:** Thresholds pre-registered; universe not frozen yet.

The 20-stock V0 universe must be selected mechanically and committed before B001
results are viewed.

## Candidate Source

The starting candidate set is the Nifty 100 constituent list as of the universe
freeze date. This is intentionally survivorship-biased and not point-in-time.
The source file or page used for the constituent list must be saved or cited in
the universe-freeze artifact.

## Fixed Windows

```text
research_period:   2016-01-01 through 2022-12-31, inclusive
validation_period: 2023-01-01 through 2026-08-19, inclusive
full_window:       2016-01-01 through 2026-08-19, inclusive
```

Special sessions are excluded from research-bar eligibility under D-029.

## Mechanical Filters

Apply these filters in this order:

1. Keep only candidates with NSE daily market-data rows in `EQ` series.
2. Exclude any candidate with an `UNSUPPORTED` corporate action in the full
   window unless deterministic support is added before universe selection.
3. Exclude any candidate whose first valid ordinary-session EQ bar is after
   2016-01-29.
4. Exclude any candidate without a valid ordinary-session EQ bar on 2026-08-19.
5. Exclude any candidate with valid-bar coverage below 98% of expected ordinary
   sessions in either the research period or validation period.
6. Exclude any candidate with more than 5 consecutive missing ordinary-session
   bars anywhere in the full window.
7. Exclude any candidate whose research-period median daily raw traded value is
   below INR 250,000,000.

If fewer than 20 candidates pass these filters, halt universe construction and
record a new decision before changing any threshold.

## Liquidity Ranking

Liquidity ranking uses the research period only. Rank surviving candidates by
descending median daily raw traded value over valid ordinary-session bars from
2016-01-01 through 2022-12-31.

Raw traded value means the exchange-provided raw traded-value field:

- legacy CM bhavcopy: `TOTTRDVAL`;
- CM-UDiFF: `TtlTrfVal`.

Do not rank liquidity from adjusted price multiplied by adjusted volume. If a
trusted exchange traded-value field is absent or non-positive for a row, that row
is a data-quality issue and does not contribute to the median.

## Selection And Tie-Breaks

Select the top 20 candidates after filtering and liquidity ranking.

Tie-break order:

1. higher research-period median daily raw traded value;
2. higher research-period valid-bar count;
3. alphabetical `symbol`.

No discretionary substitutions are allowed.

## Missing-Bar Policy For Future Backtests

A missing bar that survives the above universe-level tolerance is handled by the
backtester as follows:

- the symbol is ineligible for new entry or rebalance execution on that session;
- if already held, the position is marked using the most recent valid close and
  cannot be traded until the next valid bar;
- a gap longer than 5 consecutive ordinary sessions halts the run for data
  review.

This policy is pre-registered here because missing bars affect both universe
construction and future portfolio accounting.

The universe-freeze artifact must report:

- Nifty 100 source and freeze date;
- candidate count before any filter;
- symbols excluded by unsupported corporate actions;
- excluded action purposes and dates;
- candidate count after corporate-action exclusion;
- symbols excluded by history, missing-bar, and liquidity filters;
- candidate count after all filters;
- selected 20 symbols with research-period median raw traded value and valid-bar
  coverage.

Every V0 report must label these known universe biases:

```text
SURVIVORSHIP-BIASED: YES
POINT-IN-TIME UNIVERSE: NO
UNSUPPORTED-CORPORATE-ACTION FILTER: YES
```
