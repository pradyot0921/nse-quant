# Project Decision Log

**Project:** NSE Quant Research and Trading System  
**Purpose:** Record changes to frozen project rules so research decisions remain auditable.

---

## How to use this file

Create a new entry whenever a frozen specification changes.

Do not rewrite old entries to make the project look cleaner in hindsight.

Each entry should record:

- Decision ID
- Date
- Status
- Old rule
- New rule
- Reason
- Affected experiment IDs
- Rerun required?
- Notes

---

## D-001 — Initial market scope

**Date:** 19 August 2026  
**Status:** Accepted

**Decision:** V0/V1 uses NSE cash equity delivery, long/cash only. Intraday, F&O, leverage, overnight cash-equity shorts, and live trading are excluded.

**Affected experiments:** All V0/V1 experiments  
**Rerun required:** No

---

## D-002 — AI outside trading path

**Date:** 19 August 2026  
**Status:** Accepted

**Decision:** LLMs may assist research/documentation later but are excluded from deterministic data, accounting, risk, cost, and execution logic.

**Affected experiments:** All  
**Rerun required:** No

---

## D-003 — B001 weekly rebalance

**Date:** 19 August 2026  
**Status:** Accepted

**Old rule:** B001 ranking frequency unspecified.  
**New rule:** Evaluate B001 once per week after the final NSE trading session closes. Resulting orders execute no earlier than the next NSE trading session open.

**Reason:** Prevent rank-boundary churn and make turnover behaviour deterministic before the first run.

**Affected experiments:** B001 and direct variants  
**Rerun required:** No, decision made before first run

---

## D-004 — Turnover is a post-run gate

**Date:** 19 August 2026  
**Status:** Accepted

**Old rule:** Wording could be interpreted as blocking trades once the annual ceiling was reached.  
**New rule:** The engine never blocks the 31st round trip. It records all strategy-required trades. Each complete calendar year is evaluated after the run against the ≤30 round-trip mandate.

**Reason:** Avoid calendar-counter path dependence.

**Affected experiments:** B001 and other V0/V1 strategy specifications  
**Rerun required:** No, decision made before first run

---

## D-005 — Current fee schedule applied retrospectively

**Date:** 19 August 2026  
**Status:** Accepted

**Decision:** Initial historical backtests apply the dated 2026 reference fee schedule to older data. This asks whether historical signals survive approximately current costs; it is not historical fee reconstruction.

**Affected experiments:** V0/V1 historical backtests  
**Rerun required:** No

---

## D-006 — Two-position and three-position variants are separate trials

**Date:** 19 August 2026  
**Status:** Accepted

**Decision:** Because fixed DP charges interact with position size, 2-position and 3-position implementations must be recorded as separate specifications/trials.

**Affected experiments:** B001 variants  
**Rerun required:** No

---

## D-007 — Research drawdown is benchmark-relative

**Date:** 19 August 2026  
**Status:** Accepted

**Old rule:** A provisional absolute 20% maximum-drawdown research gate.

**New rule:** Historical research fails the drawdown gate only when strategy maximum drawdown is worse than the Nifty 100 TRI maximum drawdown over the identical evaluation period. A lower drawdown passes the minimum drawdown gate, while overall promotion still depends on return, costs, risk-adjusted performance, turnover, and validation.

**Reason:** Severe market-wide periods can legitimately produce strategy drawdowns above 20% while still demonstrating superior downside protection.

**Affected experiments:** All research candidates  
**Rerun required:** No, decision made before first strategy run

---

## D-008 — Future live-account drawdown limit is 15%

**Date:** 19 August 2026  
**Status:** Accepted

**Decision:** Future live deployment uses a separate absolute account-level maximum drawdown of 15% from the live equity high-water mark. Reaching the limit stops new entries and automated trading pending human review.

**Reason:** Live loss tolerance and historical strategy quality are different risk questions.

**Affected experiments:** None; applies to future live deployment  
**Rerun required:** No

---

## D-009 — B003 hysteresis is pre-registered

**Date:** 19 August 2026  
**Status:** Accepted

**Decision:** Before B001 runs, register B003 as the planned turnover-response specification: enter at rank 3 or better, continue holding while rank is 6 or better, and exit below rank 6 or on ineligibility, evaluated weekly.

**Reason:** Prevent choosing a churn-reduction rule after observing B001 turnover.

**Affected experiments:** B001/B003  
**Rerun required:** No

---

## D-010 — Turnover fails on any complete calendar year

**Date:** 19 August 2026  
**Status:** Accepted

**Decision:** A specification fails the ≤30 round-trip turnover mandate if any complete calendar year exceeds 30. Partial first/last years are reported but excluded from PASS/FAIL and are not annualised.

**Reason:** Makes multi-year aggregation deterministic and avoids small-sample annualisation distortion.

**Affected experiments:** B001, B002, B003 and other V0/V1 strategies  
**Rerun required:** No

---

## D-011 — Decimal prices at ingestion

**Date:** 19 August 2026  
**Status:** Accepted

**Decision:** Monetary OHLC and execution/reference prices are converted to `Decimal` during data ingestion/normalisation before they enter the backtester. Daily NAV uses exact Decimal arithmetic at the documented accounting precision.

**Reason:** Preserve meaningful accounting invariants and avoid hiding errors behind floating-point tolerances.

**Affected experiments:** All  
**Rerun required:** No

---

## D-012 — Full exits and retry on unfillable exit

**Date:** 19 August 2026  
**Status:** Accepted

**Decision:** Entry quantities may be resized downward at the actual T+1 fill price to avoid negative cash. Exit orders always target the full held quantity and are never price-resized. If an exit cannot execute at all because the execution model has no valid trade, the position is carried forward and the full exit is retried on the next eligible session.

**Reason:** Prevent accidental stub holdings and define rare gap/circuit/no-trade behaviour before implementation.

**Affected experiments:** All backtests and future paper/live execution  
**Rerun required:** No

---

## D-013 — Fill-level cost allocation is reporting-only

**Date:** 19 August 2026  
**Status:** Accepted

**Old rule:** The cost engine produced an authoritative daily aggregate but did not define how daily charges would be attributed to fills or symbols for trade logs and manual reconciliation.

**New rule:** Daily cost totals remain the authoritative accounting unit. Fill-level and symbol-level costs are reporting allocations only. DP charges are assigned directly to sold symbols and, when a symbol has multiple same-day sell fills, allocated across those fills pro-rata by that symbol's sell turnover. All other components are allocated pro-rata by turnover within the applicable side: buy-side STT and stamp duty across buy fills, sell-side STT across sell fills, and brokerage, exchange transaction charges, SEBI charges, and GST across all fills by turnover. Allocated component totals must sum back exactly to the authoritative daily component totals.

**Reason:** Phase 1 requires itemised trade logs and at least one manually reconciled trade, while STT and some other charges are rounded or aggregated at the day level. Defining allocation now prevents arbitrary per-trade reporting later.

**Affected experiments:** All backtests and reports  
**Rerun required:** No, decision made before first strategy run

---

## D-014 — Initial adverse slippage assumptions

**Date:** 19 August 2026  
**Status:** Accepted

**Old rule:** Slippage direction was defined as adverse and deterministic, but the initial rate was not frozen in the experiment ledger.

**New rule:** The baseline adverse deterministic slippage assumption is 0.05%. A 0.15% adverse deterministic robustness run is pre-registered separately and must not be selected or discarded after viewing baseline results.

**Reason:** Slippage is a research parameter and must be fixed before data-driven results are viewed.

**Affected experiments:** B001, B002, B003 and their slippage robustness variants  
**Rerun required:** No, decision made before first strategy run

---

## D-015 — DP charges use provisional aggregate pre-GST base

**Date:** 19 August 2026  
**Status:** Accepted

**Old rule:** The Zerodha reference profile stored GST-inclusive DP values per sold stock and multiplied that rounded amount by the number of distinct sold symbols.

**New rule:** The Zerodha reference profile stores pre-GST DP bases: ₹13.00 for a male primary holder and ₹12.75 for a female primary holder. For each trading day, aggregate the applicable pre-GST DP base across distinct sold symbols, apply GST once to that aggregate, and round the final DP charge to paise. DP GST remains inside `dp_charges` and is not included in the normal brokerage/exchange/SEBI GST component.

**Reason:** The per-symbol GST-inclusive ordering and aggregate-then-GST ordering differ by paise for the female-primary profile. The project chooses the aggregate-then-GST interpretation for now because it keeps the pre-GST DP base explicit, but this remains provisional pending reconciliation against a real Zerodha delivery funds statement or contract note. The observed discrepancy is one to three paise and is below the ₹1 daily cost-engine acceptance tolerance.

**Affected experiments:** All backtests and reports using DP charges  
**Rerun required:** No, decision made before first strategy run

---

## D-016 — Corporate-action adjustment precision and combined events

**Date:** 19 August 2026  
**Status:** Accepted

**Old rule:** Corporate-action split and bonus support did not specify adjusted-price precision, adjusted-volume precision, or how to handle a single NSE purpose string containing both a split and a bonus.

**New rule:** Corporate-action factors are `Decimal` values quantized to 10 decimal places using `ROUND_HALF_UP`. Adjusted OHLC prices are quantized to `Decimal("0.000001")` rupees after applying cumulative factors. Adjusted volume is adjusted alongside price and quantized to six decimal places. A combined split-plus-bonus purpose string is unsupported in V1 and must be quarantined until the parser can represent multiple actions on one ex-date.

**Reason:** Bonus ratios such as 1:2 create repeating decimal price factors, and leaving their precision implicit would leak context-dependent Decimal values into later accounting. Combined split-plus-bonus strings cannot be represented safely by the current one-record/one-action parser and must not silently drop either action.

**Affected experiments:** Corporate-action adjustment, data loader, universe construction, and all downstream backtests  
**Rerun required:** No, decision made before first corporate-action validation run

---

## D-017 — Ignored corporate actions and validation gate

**Date:** 19 August 2026  
**Status:** Accepted

**Old rule:** Unsupported corporate actions covered both recognised no-op records such as dividends and genuinely unsafe or ambiguous corporate-action text. `factors_for_date()` raised when it encountered any unsupported action for the symbol.

**New rule:** Known no-price-adjustment events parse as `IGNORED` with neutral price and volume factors. This includes dividends, AGMs, EGMs, board meetings, and name changes. Genuinely unrecognised, ambiguous, or price-continuity-affecting events remain `UNSUPPORTED`. Dataset construction must call `validate_actions()` once for the frozen symbol set and date range, and must halt or quarantine if unsupported matching actions are present. `factors_for_date()` is a pure factor lookup that assumes validated input.

**Reason:** Dividends are common in large-cap Indian equities and should not block price-series adjustment when V0 explicitly does not dividend-adjust. At the same time, silently ignoring unknown events would risk corrupting historical prices. Splitting ignored from unsupported actions keeps the parser conservative without making real NSE corporate-action files unusable.

**Affected experiments:** Corporate-action adjustment, data loader, universe construction, and all downstream backtests  
**Rerun required:** No, decision made before first corporate-action validation run

---

## D-018 — Real NSE corpus-derived corporate-action parser rules

**Date:** 19 August 2026
**Status:** Accepted

**Old rule:** Split parsing supported synthetic face-value wording but did not support the actual NSE `Face Value Split (Sub-Division)` wording containing `Per Share`. Scheme-of-arrangement bonus-like records and several non-equity bonus instruments were not explicitly classified.

**New rule:** V1 explicitly supports the seven observed NSE EQ-series face-value split formats identified in the 19-Aug-2025 to 19-Aug-2026 corpus. Any `Scheme Of Arrangement` record is `UNSUPPORTED` in V1. Bonus NCRPS, NCD, CRPS, OCRPS, debentures, preference shares, warrants, and other non-equity bonus instruments are `UNSUPPORTED`.

**Evidence:** One-year NSE EQ corporate-action corpus scan after correction:

SPLIT=52
BONUS=49
IGNORED=1683
UNSUPPORTED=82

**Reason:** Real-data validation exposed 52 safe false-negative split records and one unsafe false-positive NCRPS adjustment before adjusted OHLCV data was constructed. The TVSMOTOR `Scheme Of Arrangement - Bonus Ncrps 4:1` record would have applied a 0.2 price factor to a liquid stock, fabricating a 400% single-day return that a momentum ranker could treat as the strongest signal in the universe. The parser's unit tests passed throughout because they encoded the same invented wording as the code. The rules were updated from observed NSE production wording rather than invented examples.

**Affected experiments:** Corporate-action adjustment, data loader, universe construction, and all downstream backtests
**Rerun required:** No completed strategy runs exist; rerun the corporate-action corpus scan before universe freeze

---

## D-019 — Corporate-action convention validation and V0 exclusion rules

**Date:** 19 August 2026
**Status:** Accepted

**Old rule:** Bonus ratio convention was inferred from market convention but not validated against raw NSE price data. Buybacks were classified as `UNSUPPORTED`. V0 did not explicitly state how rights issues affect universe selection. The data-validation layer did not define an independent check for corporate-action records missing from the NSE corporate-action file.

**New rule:** NSE bonus ratios are interpreted as new shares per existing shares: `Bonus X:Y` means X new shares for Y held shares. Buyback records labelled `Buy Back` are `IGNORED` for price and volume adjustment because neither tender-offer buybacks nor open-market buybacks multiply or dilute the holdings of non-participating shareholders. V0 excludes any symbol with a rights issue inside the research window from the frozen universe unless a later decision adds deterministic rights adjustment support. During OHLCV validation, an ISIN change from the prior session with no same-date split, bonus, unsupported action, or identifier-changing ignored action such as a name change must halt or quarantine the symbol/date as a possible missing corporate action. Dividends, AGMs, EGMs, and board meetings do not explain an ISIN change.

**Evidence:** Official NSE CM-UDiFF bhavcopy checks:

- PATANJALI `Bonus 2:1`, ex-date 11 September 2025: prior close 1802.00, ex-date open 602.70. Correct convention predicts 600.67, a 0.34% difference; inverted convention predicts 901.00, a 33.11% difference.
- BEML face-value split 10 to 5, ex-date 3 November 2025: prior close 4399.80, ex-date open 2188.00. The 0.5 split factor predicts 2199.90, a 0.54% difference.
- INFY `Buy Back`, ex-date 14 November 2025: ten sessions either side showed ordinary market movement rather than a mechanical adjustment step. This corroborates, but does not replace, the structural no-entitlement-change reason for ignoring buybacks.
- The seven real split examples from the 19-Aug-2025 to 19-Aug-2026 corpus all changed ISIN on the split ex-date in official NSE CM-UDiFF bhavcopy data.

**Reason:** The split and bonus price checks remove the final parser convention ambiguity using raw exchange bhavcopy data rather than unit-test assumptions. Buybacks do not create a share-count entitlement multiplier for shareholders who do not participate, so applying any automatic price/volume factor would be wrong. Rights issues do affect ex-date price continuity but are not supported in V0, so excluding affected symbols before the universe freeze prevents deadline pressure from weakening the quarantine gate. ISIN changes provide a cheap independent signal that can catch missing corporate-action records before adjusted OHLCV is trusted, but no-op records that cannot change identifiers must not mask missing split or bonus records.

**Affected experiments:** Corporate-action adjustment, data loader, universe construction, and all downstream backtests
**Rerun required:** No completed strategy runs exist; rerun the corporate-action corpus scan and price-continuity checks before universe freeze

---

## D-020 — Universe liquidity ranking uses raw traded value

**Date:** 19 August 2026
**Status:** Accepted

**Old rule:** V0 universe selection required high median daily traded value but did not specify whether traded value is computed from raw or adjusted OHLCV fields when an explicit turnover field is unavailable.

**New rule:** Universe selection ranks liquidity using the exchange-provided raw traded value or, if unavailable, raw close multiplied by raw volume. Do not compute median daily traded value from adjusted price multiplied by adjusted volume.

**Reason:** Traded value is economically invariant: the rupees exchanged on a historical session are the raw price-volume product for that session. Adjusted price multiplied by adjusted volume should be close but can drift because both adjusted fields are quantized, adding needless imprecision to universe ranking.

**Affected experiments:** Universe construction, data validation, and all downstream Phase 1 backtests
**Rerun required:** No universe has been frozen yet.

---

## D-021 — Full-window corporate-action exclusion before V0 universe freeze

**Date:** 19 August 2026
**Status:** Accepted

**Old rule:** The V0 universe rule excluded rights issues but did not explicitly require a full research-window corporate-action scan before freezing the 20 symbols, nor did it state how to treat other `UNSUPPORTED` actions discovered outside the one-year parser corpus.

**New rule:** Before freezing the V0 universe, run the corporate-action parser over the full intended research window for all candidate symbols. Any candidate with an `UNSUPPORTED` corporate action inside the research window is excluded from V0 unless a later decision adds deterministic support for that action type before universe selection. Report the candidate count excluded by this rule and list the excluded symbols and action purposes in the universe-freeze artifact.

**Reason:** The one-year corpus scan proved parser vocabulary, but a longer research window across Nifty 100 candidates can contain rights issues, demergers, schemes of arrangement, mergers, or other unsupported events. Excluding affected candidates before B001 results exist prevents deadline pressure from weakening the quarantine gate after partial results are visible.

**Bias note:** V0 already accepts survivorship bias. This rule adds a second explicit filter toward stable, continuously listed large caps without unsupported corporate-action events. V0 dataset labels and reports must disclose both biases.

**Affected experiments:** Universe construction, data validation, and all downstream Phase 1 backtests
**Rerun required:** No universe has been frozen yet.

---

## D-022 — NSE UDiFF loader calendar and series policy

**Date:** 19 August 2026
**Status:** Accepted

**Old rule:** The UDiFF loader did not define how to distinguish a market holiday from a missing raw file, and did not freeze the permitted security series for V0.

**New rule:** The NSE CM-UDiFF loader must receive or load a version-controlled expected trading-session calendar for the requested date range. Missing UDiFF files for expected sessions are data failures; non-session dates are not expected files. V0 loads only `EQ` series rows for equity research. Non-`EQ` rows must be rejected or reported explicitly and must not silently enter the research universe.

**Reason:** A date gap can mean a holiday, a failed download, or an unpublished file, and the loader cannot classify that without an explicit calendar. `BE` and other non-`EQ` series have different settlement or liquidity characteristics, so allowing them into the V0 universe would violate the locked market scope and liquidity assumptions.

**Affected experiments:** UDiFF loader, data validation, universe construction, and all downstream Phase 1 backtests
**Rerun required:** No market-data pipeline or universe has been frozen yet.

---

## D-023 — Version-controlled NSE trading-session calendar source

**Date:** 20 August 2026
**Status:** Accepted

**Old rule:** D-022 required a version-controlled expected trading-session calendar but did not define the calendar source, extension process, or treatment of special sessions.

**New rule:** The V0 expected-session calendar is a checked-in artifact generated from NSE's published Capital Market trading-holiday list for each calendar year, weekends, and explicitly recorded special-session exceptions such as Muhurat trading. The checked-in session file is the loader's source of truth at runtime. NSE holiday pages, attachments, and circulars are provenance inputs, not runtime dependencies.

If a UDiFF file exists on a date absent from the checked-in calendar, the loader must report a calendar mismatch and halt or quarantine until the date is either documented as a special session or rejected as out of scope. If an expected session has no raw UDiFF file, the loader treats that as a data failure. New years are added by committing the holiday source, generated session list, and any known special sessions before that year enters a research run.

**Reason:** Deriving the expected calendar from observed UDiFF file existence is circular because file presence is exactly what the loader must validate. NSE can also open special sessions outside the ordinary weekday-minus-holidays pattern, so those exceptions need explicit provenance rather than ad hoc runtime loosening.

**Affected experiments:** UDiFF loader, data validation, universe construction, and all downstream Phase 1 backtests
**Rerun required:** No market-data pipeline or universe has been frozen yet.

---

## D-024 — NSE UDiFF traded value uses TtlTrfVal

**Date:** 20 August 2026
**Status:** Accepted

**Old rule:** D-020 required universe liquidity ranking to use exchange-provided raw traded value where available, with raw close multiplied by raw volume as a fallback, but did not name the NSE CM-UDiFF traded-value field.

**New rule:** For NSE CM-UDiFF input, `TtlTrfVal` is the authoritative raw traded value field for liquidity ranking and validation. The raw close multiplied by raw volume fallback may be used only when a non-UDiFF source lacks a reliable traded-value field or when a source-specific validation record explicitly documents that the field is absent or unusable. In normal CM-UDiFF files, missing, blank, zero, or non-positive `TtlTrfVal` is a data-quality event rather than a reason to silently fall back.

**Evidence:** In the 31 October 2025 CM-UDiFF file, BEML has `TtlTrfVal=1554003341.40`, while `ClsPric * TtlTradgVol = 4399.80 * 349959 = 1539749608.20`, a 0.9172% understatement. The implied traded-value VWAP is 4440.53, which sits between the day's official low 4382.90 and high 4505.00.

**Reason:** Close multiplied by volume is not traded value; it replaces the session's actual turnover with a closing-price approximation. Since CM-UDiFF supplies the true traded-value field, V0 should use it directly and avoid systematic liquidity-ranking error.

**Affected experiments:** UDiFF loader, data validation, universe construction, and all downstream Phase 1 backtests
**Rerun required:** No market-data pipeline or universe has been frozen yet.

---

## D-025 — No-trade UDiFF rows are not tradeable OHLCV bars

**Date:** 20 August 2026
**Status:** Accepted

**Old rule:** The loader policy for NSE CM-UDiFF rows with zero volume, zero traded value, or zero/blank OHLC prices was unspecified. `OHLCVBar` requires positive OHLC values.

**New rule:** A CM-UDiFF `EQ` row with non-positive `TtlTradgVol` or non-positive `TtlTrfVal` is not a valid tradeable OHLCV bar in V0. The loader must report or quarantine the symbol/date and must not carry prices forward, fabricate OHLC values, or allow such a row into execution simulation. Zero, blank, or non-positive OHLC fields in an `EQ` row are data-quality failures for V0 bar construction. Universe selection must treat missing valid tradeable bars inside the required lookback or research window as an exclusion unless a later decision defines a different missing-bar policy.

**Evidence:** The five inspected CM-UDiFF files dated 10 September 2025, 11 September 2025, 31 October 2025, 3 November 2025, and 13 July 2026 contained no zero-volume rows, including no zero-volume `EQ` rows. This is limited sample evidence, not proof that suspended, halted, or otherwise untraded rows cannot appear across the full research window. The policy is therefore pre-registered before encountering the failure mode in the loader.

**Reason:** A zero-volume row cannot represent an executable session for the strategy. Carrying forward prices would invent tradable data, while allowing zero prices would violate the positive-price invariant already enforced by `OHLCVBar`.

**Affected experiments:** UDiFF loader, data validation, universe construction, execution simulation, and all downstream Phase 1 backtests
**Rerun required:** No market-data pipeline or universe has been frozen yet.

---

## D-026 — CM-UDiFF traded-value VWAP range invariant

**Date:** 20 August 2026
**Status:** Accepted

**Old rule:** D-024 made `TtlTrfVal` the authoritative CM-UDiFF traded-value field but did not define a row-level integrity check for field misalignment, unit changes, or corrupted traded-value data.

**New rule:** For every valid CM-UDiFF `EQ` row, `TtlTrfVal / TtlTradgVol` must lie inside the inclusive daily low/high range after a half-paisa absolute tolerance on price: `LwPric - 0.005 <= implied_vwap <= HghPric + 0.005`. A violation is a data-quality failure for that row/file and must not silently fall back to close multiplied by volume.

**Evidence:** In the 31 October 2025 CM-UDiFF file, BEML has `TtlTrfVal=1554003341.40` and `TtlTradgVol=349959`, implying VWAP 4440.53, which lies between official low 4382.90 and high 4505.00.

**Reason:** The invariant is a cheap check that the raw traded-value and volume fields are aligned with the OHLC fields. It catches likely schema shifts, unit changes, or row corruption before liquidity ranking or validation consumes the data. The half-paisa tolerance allows harmless two-decimal traded-value rounding at the price boundary without weakening the check enough to mask a real unit or schema error.

**Affected experiments:** UDiFF loader, data validation, universe construction, and all downstream Phase 1 backtests
**Rerun required:** No market-data pipeline or universe has been frozen yet.

---

## D-027 — Missing tradeable-bar tolerance and mid-position handling

**Date:** 20 August 2026
**Status:** Accepted

**Old rule:** D-025 stated that a missing valid tradeable bar inside the lookback or research window is an exclusion, but did not define tolerance. Taken literally, a single halted session across a decade would exclude an otherwise usable large-cap candidate.

**New rule:** V0 universe candidates may have a small number of missing or invalid tradeable `EQ` bars, but only within both limits: no more than 0.5% of expected trading sessions in the research window, and no run longer than 3 consecutive expected sessions. The universe-freeze artifact must report every missing or invalid symbol/date counted under this rule. A candidate exceeding either limit is excluded before B001 results are viewed.

In the backtester, a missing valid bar for a held symbol means no fill can occur for that symbol on that session. Pending exits remain pending and retry on the next valid tradeable bar, consistent with D-012. NAV may use the last valid adjusted close for mark-to-market on the missing session only with an explicit stale-price flag in reporting; this does not create an OHLCV bar, execution price, or volume. A missing bar for a candidate not currently held makes that symbol ineligible for new entry on that rebalance date.

**Reason:** Isolated halts or data-quality gaps should not automatically remove a large-cap candidate from a decade-long V0 study, but prolonged suspension or repeated missing data changes the research object. Separating loader bar construction from backtester stale valuation keeps reproducibility without inventing tradeable prices.

**Affected experiments:** UDiFF loader, data validation, universe construction, backtester, execution simulation, reporting, and all downstream Phase 1 backtests
**Rerun required:** No market-data pipeline, universe, or strategy run has been frozen yet.

---

## D-028 — CM-UDiFF row-level rejection model

**Date:** 20 August 2026
**Status:** Accepted

**Old rule:** `parse_cm_udiff_file()` raised on the first invalid `EQ` row. A single malformed row therefore destroyed the entire trading day, even though D-025 specified reporting or quarantining the symbol/date.

**New rule:** CM-UDiFF file-level failures still raise immediately: unexpected schema, empty file, multiple `TradDt` values, multiple `BizDt` values, `TradDt != BizDt`, or filename/trade-date mismatch. Row-level `EQ` failures are collected as immutable rejected rows containing row number, symbol, series, and reason. Valid `EQ` bars from the same file remain available to callers. Downstream validation decides policy: fail if rejected rows exceed the missing-bar tolerance, fail if a required universe symbol is rejected, otherwise proceed with an explicit rejection log.

**Evidence:** A one-year scan of downloaded NSE CM-UDiFF files from 20 August 2025 through 19 August 2026 covered 247 files, 816,308 total rows, and 585,893 `EQ` rows. The strict row checks produced zero rejected `EQ` rows and zero file-level errors in that window. A synthetic malformed row with `PrvsClsgPric=0` reproduced the structural bug: the previous parser discarded the whole day, while the new parser quarantines only the bad symbol/date.

**Reason:** Recent real data suggests the row checks are not noisy, but a decade-long run across millions of rows should not lose a full trading session because one non-universe or otherwise isolated symbol has a malformed row. Keeping row failures explicit preserves auditability while allowing universe and backtest policy to make the research-relevant decision.

**Affected experiments:** UDiFF loader, data validation, universe construction, backtester, reporting, and all downstream Phase 1 backtests
**Rerun required:** No market-data pipeline, universe, or strategy run has been frozen yet.

---

## D-029 — Special sessions are audited but excluded from V0 research bars

**Date:** 20 August 2026  
**Status:** Accepted

**Old rule:** The checked-in NSE CM session calendar distinguished `NORMAL` and `SPECIAL` sessions, but did not define whether special sessions should enter the research bar series used for lookbacks, signal generation, or simulated execution.

**New rule:** V0 keeps special sessions in the checked-in calendar for raw CM-UDiFF file auditing. A missing raw file for a special session is still a data-acquisition problem, and a raw file on an unlisted date is still a calendar mismatch. By default, research bar construction uses only `NORMAL` sessions. Special sessions enter a research run only through an explicit opt-in parameter and must be labelled in any resulting dataset/report.

**Evidence:** The 20-Aug-2025 to 19-Aug-2026 calendar contains two special sessions: 21 October 2025 Diwali Muhurat trading and 1 February 2026 Union Budget Sunday trading. The 21 October 2025 Muhurat CM-UDiFF file was inspected directly: it contains 2,291 `EQ` rows and uses `SsnId=F1`, the same session identifier observed in normal-session files. `SsnId` therefore cannot be relied on to identify special sessions; the checked-in calendar is the source of truth.

**Reason:** Muhurat and other special sessions have unusual timing, liquidity, and market context. Counting them as ordinary daily bars would let a short symbolic or otherwise abnormal session affect momentum lookbacks, rebalance observations, and next-session execution by omission. Keeping them in acquisition auditing preserves raw-data completeness while excluding them from default research avoids silently changing the meaning of a trading day.

**Affected experiments:** UDiFF loader, data validation, universe construction, B001/B002/B003, backtester, reporting, and all downstream Phase 1 backtests.

**Rerun required:** No market-data pipeline, universe, or strategy run has been frozen yet.

---

## D-030 — Phase 1 research window and validation split

**Date:** 22 August 2026
**Status:** Accepted

**Old rule:** The Phase 1 experiment ledger left `research_period` and `validation_period` as `TBD`. The project required a full intended research window before universe freeze, but had not fixed the start date, end date, train/validation split, or the status of the validation block after inspection.

**New rule:** Phase 1 V0 experiments use:

- research/training period: 1 January 2016 through 31 December 2022, inclusive;
- validation period: 1 January 2023 through 19 August 2026, inclusive;
- full V0 data-audit window: 1 January 2016 through 19 August 2026, inclusive.

The 2023-2026 validation block is a one-time holdout for Phase 1 B001/B002/B003 evaluation. Once inspected for strategy performance, it is contaminated for future selection or parameter tuning. Later research that needs fresh unseen evidence must use newly accumulated post-19-August-2026 market data as the next frontier, or explicitly label any reuse of the 2023-2026 block as in-sample/previously inspected.

**Reason:** The split is fixed before full-window data download, universe selection, or any B001/B002/B003 result exists. The 2016 start is chosen because NSE's trading-holiday API has been verified to return historical CM holiday data for 2011 through 2026, including 2016, making an independently derived calendar feasible from the chosen start. The project deliberately does not extend the initial V0 window back to 2011 because the current parser and corpus evidence are built around modern CM-UDiFF files and the pre-UDiFF historical-source bridge has not yet been specified or validated. Starting in 2016 still gives seven complete calendar years for data validation, universe construction, and baseline development, while avoiding an even larger legacy-data commitment before the source bridge is designed. The 2023-2026 validation period gives a materially later multi-year block while ending at the already established 19-August-2026 data-audit cutoff. These dates are not chosen from observed strategy performance; no such results exist.

**Affected experiments:** B001, B001-S015, B002, B002-S015, B003, B003-S015, universe construction, data validation, and all downstream Phase 1 reports.

**Rerun required:** No. No full-window data build, universe freeze, or strategy run exists yet.

---

## D-031 — Historical market-data source bridge

**Date:** 23 August 2026
**Status:** Accepted

**Old rule:** Phase 0 and Phase 1 described NSE CM-UDiFF Common Bhavcopy Final as the primary raw daily-market source, but D-030 fixed a V0 data-audit window beginning on 1 January 2016. UDiFF is the current format and does not by itself cover the whole pre-2024 research window.

**New rule:** V0 uses two official NSE daily-market source families normalized into one canonical daily-bar schema:

- 1 January 2016 through 5 July 2024: NSE `Full Bhavcopy and Security Deliverable data`;
- 8 July 2024 through 19 August 2026: NSE `CM-UDiFF Common Bhavcopy Final`.

The 6-7 July 2024 weekend has no expected normal cash-market session. If a later checked-in calendar identifies a special session on either date, that date must be handled by an explicit source note before dataset construction.

Both source families must preserve raw files unchanged and normalize into the same processed fields: trade date, source format, symbol, security series, optional ISIN, raw OHLC, previous close, raw traded volume, raw traded value, and any source-specific audit fields. For CM-UDiFF, `TtlTrfVal` remains authoritative. For the legacy full-bhavcopy source, raw traded value is provisionally `TURNOVER_LACS * 100000`, pending real-file validation before parser implementation.

The legacy source is expected to lack ISIN. Therefore the ISIN-continuity guard from D-019 applies only on dates whose normalized rows contain ISIN. Pre-UDiFF missing-corporate-action detection relies on the NSE corporate-action file, full-window corporate-action scan, raw-versus-adjusted continuity checks, and explicit unsupported-action exclusion.

Before implementing the legacy parser, inspect real legacy files from at least 2016, 2019, 2020, 2022, and July 2024. Record headers, row counts, series counts, traded-value units, no-trade rows, and row-quality failures in a validation artifact. Do not infer the legacy schema from UDiFF or from invented rows.

**Evidence:** NSE's All Reports page lists `CM-UDiFF Common Bhavcopy Final (zip)` as the current CM bhavcopy source and states that older `CM - Bhavcopy(csv)` and `CM - Common Bhavcopy (csv)` reports were discontinued with effect from 8 July 2024. The same reports page lists `Full Bhavcopy and Security Deliverable data`, which is the selected official NSE bridge source for pre-UDiFF daily cash-equity bars.

**Reason:** D-030 made the historical window concrete. Treating UDiFF as the only source would leave 2016 through early July 2024 undefined; silently choosing a legacy source during implementation would reintroduce an unregistered data decision. The full-bhavcopy bridge keeps the project on official NSE daily data, preserves traded value and delivery fields useful for liquidity validation, and forces real-file schema validation before code is written.

**Affected experiments:** UDiFF loader, legacy daily-market loader, data validation, universe construction, B001, B001-S015, B002, B002-S015, B003, B003-S015, and all downstream Phase 1 reports.

**Rerun required:** No. No full-window data build, universe freeze, or strategy run exists yet.

---

## D-032 — Legacy market-data bridge uses CM bhavcopy ZIP

**Date:** 23 August 2026
**Status:** Accepted

**Old rule:** D-031 selected NSE `Full Bhavcopy and Security Deliverable data` as the pre-UDiFF source bridge for 1 January 2016 through 5 July 2024, with raw traded value provisionally mapped from `TURNOVER_LACS * 100000` and legacy ISIN expected to be unavailable.

**New rule:** The pre-UDiFF V0 source bridge uses NSE `CM - Bhavcopy(csv)` historical ZIP files:

```text
https://nsearchives.nseindia.com/content/historical/EQUITIES/YYYY/MMM/cmDDMMMYYYYbhav.csv.zip
```

for 1 January 2016 through 5 July 2024. Each legacy ZIP must contain exactly one CSV. The observed canonical mapping is: `TIMESTAMP` to trade date, `SYMBOL`, `SERIES`, `ISIN`, `OPEN`, `HIGH`, `LOW`, `CLOSE`, `LAST`, `PREVCLOSE`, `TOTTRDQTY`, `TOTTRDVAL`, and `TOTALTRADES`. Legacy raw traded value is `TOTTRDVAL` in rupees, not `TURNOVER_LACS * 100000`. Delivery quantity and delivery percentage are not present in this source and must remain absent/null rather than fabricated.

The D-019 ISIN-continuity guard applies to the legacy CM bhavcopy segment because the scanned legacy files include non-blank ISIN for every inspected EQ row.

**Evidence:** `docs/validation/LEGACY_CM_BHAVCOPY_FORMAT_SCAN_V0.md` scanned five real NSE legacy CM bhavcopy ZIPs from 2016, 2019, March 2020, 2022, and 5 July 2024. All five downloaded successfully, had the same header, contained exactly one CSV, had non-blank EQ ISIN values, had no duplicate EQ symbols, and had zero observed `TOTTRDVAL / TOTTRDQTY` low/high range breaches. The provisional `sec_bhavdata_full_DDMMYYYY.csv` source returned 404 for the tested 2016 and 2019 dates, so it cannot be the full-window V0 bridge.

**Reason:** The first real legacy-source scan falsified D-031's source assumption before implementation. The older CM bhavcopy ZIP covers the required 2016 and 2019 dates and includes ISIN plus raw traded value in rupees, making it a stronger bridge source for V0 than the provisional full-bhavcopy choice.

**Affected experiments:** Legacy daily-market loader, data validation, universe construction, B001, B001-S015, B002, B002-S015, B003, B003-S015, and all downstream Phase 1 reports.

**Rerun required:** No. No full-window data build, universe freeze, or strategy run exists yet.

## D-033 — Batch market-data acquisition reports full-window outcomes

**Date:** 23 August 2026
**Status:** Accepted

**Old rule:** Per-file UDiFF and legacy acquisition helpers downloaded or reused one archive at a time. The policy for a decade-scale batch run was unspecified, including whether to halt at the first missing archive or corrupt cached file.

**New rule:** Full-window raw market-data acquisition is a batch orchestration layer above the source-specific per-file helpers. For each checked-in expected session, the batch chooses the registered source family from D-032, attempts acquisition, and records one of: downloaded/reused/redownloaded, archive missing, or acquisition failed. A 404 for an expected session is recorded and the batch continues so all gaps can be resolved together. If an existing cached archive fails ZIP validation, the batch deletes that archive only after verifying it is inside the configured raw-data root, then attempts one fresh download. If that fresh download also fails, the session is recorded as failed rather than silently skipped.

Raw-file auditing remains calendar-driven: expected archives come from the checked-in session calendar and source bridge; files present for dates outside that expectation are reported as unexpected archives.

**Reason:** Full-window acquisition covers roughly 2,500 sessions. Halting on the first missing archive would discover gaps one at a time, while trusting existing paths would let interrupted partial downloads become permanent raw data. Recording all outcomes preserves strict raw-file validation without making long resumable downloads fragile.

**Affected experiments:** UDiff acquisition, legacy acquisition, data validation, universe construction, B001, B001-S015, B002, B002-S015, B003, B003-S015, and all downstream Phase 1 reports.

**Rerun required:** No. No full-window data build, universe freeze, or strategy run exists yet.
