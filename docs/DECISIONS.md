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

---

## D-034 — Legacy and UDiFF normalize through one canonical equity bar

**Date:** 24 August 2026
**Status:** Accepted

**Old rule:** D-031 required both source families to normalize into one processed daily-bar schema, but the code still exposed separate `LegacyBhavcopyEquityBar` and `UDiffEquityBar` dataclasses with no shared canonical representation. The July 2024 source bridge had not been validated through same-date real-source comparison.

**New rule:** V0 normalizes both NSE `CM - Bhavcopy(csv)` legacy rows and NSE `CM-UDiFF Common Bhavcopy Final` rows into `CanonicalEquityBar`, retaining `source_format` for audit while using the same research fields: trade date, symbol, ISIN, series, OHLC, previous close, last price, traded volume, traded value, and transaction count.

The source bridge remains:

- legacy CM bhavcopy through 5 July 2024;
- CM-UDiFF from 8 July 2024 onward.

Before processed dataset construction, the July 2024 source seam must have a committed evidence artifact comparing real legacy and UDiff rows where both source families are available.

**Evidence:** `docs/validation/LEGACY_UDIFF_SEAM_VALIDATION_V0.md` checked NSE sessions from 1 July 2024 through 12 July 2024. CM-UDiFF archives were available for all 10 checked sessions. Legacy CM bhavcopy archives were available for 1-5 July 2024 and absent from 8 July 2024 onward. On the five same-date overlap sessions, every common EQ symbol matched exactly after canonical normalization: 1,914 symbols on 1 July, 1,914 on 2 July, 1,911 on 3 July, 1,910 on 4 July, and 1,906 on 5 July. Across the bridge, 8 July 2024 CM-UDiFF `previous_close` matched 5 July 2024 legacy CM bhavcopy `close` for all 1,903 common symbols.

**Reason:** The validation period contains a source-format boundary. A subtle field mapping, rounding, traded-value unit, ISIN, or volume mismatch at that boundary would contaminate both universe construction and validation-period results while looking like ordinary market data. Same-date real-source overlap gives stronger evidence than synthetic tests because it proves both parsers map production NSE rows into identical canonical bars.

**Affected experiments:** Legacy parser, UDiff parser, data validation, processed dataset construction, universe construction, B001, B001-S015, B002, B002-S015, B003, B003-S015, and all downstream Phase 1 reports.

**Rerun required:** No. No processed full-window dataset, universe freeze, or strategy run exists yet.

---

## D-035 — Market-data validation emits canonical bars and explicit problems

**Date:** 24 August 2026
**Status:** Accepted

**Old rule:** Raw-file acquisition, source-specific parsing, and canonical bar normalization existed, but there was no offline orchestration layer that combined the checked-in calendar, expected raw files, parser failures, row rejections, and canonical bars into one auditable report.

**New rule:** V0 market-data validation is an offline step over already-saved raw archives. It must not download files or freeze the universe. For every checked-in expected session, it audits whether the registered raw archive exists and reports unexpected raw archives separately. For research-bar construction it parses only sessions eligible under D-029 by default, normalizes valid EQ rows into `CanonicalEquityBar`, preserves non-EQ series counts, and records missing files, file-level parser failures, and row-level EQ rejections as explicit report fields.

Special sessions remain part of raw-file auditing. They are excluded from emitted research bars unless validation is run with an explicit opt-in.

**Reason:** The dataset builder needs one deterministic boundary between raw archives and processed daily bars. A missing file, malformed file, or rejected row must not disappear inside a parser loop, and extra raw archives from validation work, overlap scans, or special sessions must not silently enter the research dataset. Separating validation from acquisition keeps the raw-data evidence reproducible without network access.

**Affected experiments:** Raw market-data validation, processed dataset construction, universe construction, B001, B001-S015, B002, B002-S015, B003, B003-S015, and all downstream Phase 1 reports.

**Rerun required:** No. No processed full-window dataset, universe freeze, or strategy run exists yet.

---

## D-036 — Full-window corporate-action parser vocabulary updates

**Date:** 24 August 2026
**Status:** Accepted

**Old rule:** The one-year corporate-action corpus drove parser support for modern NSE split wording, ordinary bonus ratios, buybacks written as `Buy Back`, and common no-price-adjustment events. Full-window legacy vocabulary from 2016 onward had not yet been scanned.

**New rule:** V0 additionally treats `Buyback`, `Buy-Back`, `Buyback Of Shares`, and `Buy-Back Of Shares` as `IGNORED` no-price-adjustment events. Messy NSE general-meeting and book-closure variants such as `Extra Ordinary General Meeting`, `Extra-Ordinary General Meeting`, `Annual Book Closure`, and `Annual Book Closing` are also `IGNORED`. Abbreviated legacy split purposes of the form `Fv Splt Frm Rs X To Rs/Re Y` are parsed as deterministic face-value splits. Ordinary equity bonus ratios tolerate observed punctuation and spacing variants such as `Bonus 1: 1`, `Bonus- 1:2`, and `Bonus 1:1/Dividend`.

**Evidence:** The first full-window corporate-action scan for 2016-01-01 through 2026-08-19 found safe false negatives before universe selection: 127 `Buyback` records, 153 `Extra Ordinary General Meeting` records, 17 `Extra-Ordinary General Meeting` records, multiple book-closure variants, 14 abbreviated `Fv Splt Frm ...` split records, and several ordinary bonus ratios blocked only by spacing or punctuation.

**Reason:** Buybacks and meeting/book-closure notices do not mechanically multiply or dilute the holdings of non-participating shareholders and should not create needless universe exclusions. The abbreviated `Fv Splt Frm ...` strings encode the same old/new face-value relationship as already supported full split wording, so keeping them unsupported would falsely exclude symbols with deterministic split adjustments. These changes are corpus-derived and made before universe thresholds or strategy results exist.

**Affected experiments:** Corporate-action validation, adjusted OHLCV construction, universe construction, B001, B001-S015, B002, B002-S015, B003, B003-S015, and all downstream Phase 1 reports.

**Rerun required:** Completed in `docs/validation/CORPORATE_ACTION_FULL_WINDOW_SCAN_V0.md`. No universe freeze or strategy run exists yet.

---

## D-037 — V0 universe thresholds before selection

**Date:** 24 August 2026
**Status:** Accepted

**Old rule:** V0 required a mechanically selected 20-stock liquid large-cap universe before B001, but the exact liquidity, history, missing-bar, and tie-break thresholds were still pending.

**New rule:** The V0 candidate set is the Nifty 100 constituent list as of the universe freeze date. Candidates are filtered mechanically using `universes/selection_rule_v0.md`: EQ series only; no `UNSUPPORTED` corporate action in the full 2016-01-01 through 2026-08-19 window; first valid ordinary-session EQ bar no later than 2016-01-29; valid ordinary-session EQ bar on 2026-08-19; at least 98% valid-bar coverage in both the research and validation periods; no more than 5 consecutive missing ordinary-session bars; and research-period median daily raw traded value of at least INR 250,000,000. Surviving candidates are ranked by research-period median daily raw traded value, then valid-bar count, then alphabetical symbol. The top 20 are selected. If fewer than 20 candidates pass, universe construction halts until a new decision is recorded.

Missing bars that survive the universe-level tolerance are pre-registered for future backtests: no new entry or rebalance execution on a missing-bar session; if already held, mark using the most recent valid close and do not trade that symbol until the next valid bar; halt if the gap exceeds 5 consecutive ordinary sessions.

**Reason:** These thresholds are chosen before running universe selection or seeing B001 results. The INR 250,000,000 median raw traded-value floor keeps V0 focused on genuinely liquid large caps while remaining independent of strategy performance. The 98% coverage rule and 5-session gap cap avoid disqualifying a candidate for a single benign halt while still excluding materially discontinuous histories. Ranking uses research-period liquidity only so the validation period is not used to choose the 20 symbols, while full-window data-quality and corporate-action filters prevent later validation runs from failing on known unsupported events.

**Bias note:** V0 remains survivorship-biased and not point-in-time because current Nifty 100 constituents are used. The unsupported-corporate-action filter and continuous-history filter add an explicit bias toward stable, continuously listed large caps. V0 reports must disclose all three labels.

**Affected experiments:** Universe construction, processed dataset construction, B001, B001-S015, B002, B002-S015, B003, B003-S015, and all downstream Phase 1 reports.

**Rerun required:** No. No universe freeze or strategy run exists yet.

---

## D-038 — Candidate-level dividend typo records are ignored

**Date:** 24 August 2026
**Status:** Accepted

**Old rule:** The corporate-action parser ignored correctly spelled `Dividend` records but still quarantined some NSE typo or abbreviation variants such as `Int Div`, `Dividned`, and `Int Div Rs ... Per Sh`.

**New rule:** V0 treats observed dividend typo and abbreviation variants as `IGNORED` no-price-adjustment records when they clearly describe cash dividends and contain no split, bonus, rights, scheme, capital-reduction, or demerger action.

**Evidence:** The first V0 universe-freeze run excluded otherwise eligible current Nifty 100 candidates solely because of benign dividend spelling/abbreviation records: HCLTECH `Int Div- 2 Per Share (Purpose Revised)`, NESTLEIND `Interim Dividned - Rs 135 Per Share`, and TCS `Int Div Rs 4 Per Sh`.

**Reason:** Cash dividends do not mechanically multiply share count or create an OHLCV split/bonus adjustment in V0. Treating obvious dividend typo records as unsupported would add needless universe exclusions while providing no extra protection against price-series corruption. The parser still quarantines rights, schemes, demergers, capital reductions, consolidations, combined split-plus-bonus records, and non-equity bonus instruments.

**Affected experiments:** Corporate-action validation, universe construction, B001, B001-S015, B002, B002-S015, B003, B003-S015, and all downstream Phase 1 reports.

**Rerun required:** Completed in `docs/validation/NIFTY100_V0_UNIVERSE_FREEZE.md`. No strategy run exists yet.

---

## D-039 — Processed V0 dataset is a local artifact with a committed manifest

**Date:** 24 August 2026
**Status:** Accepted

**Old rule:** Raw market-data validation, corporate-action validation, and the frozen V0 universe existed, but there was no single processed dataset build step that combined them into adjusted OHLCV rows for backtesting.

**New rule:** The V0 processed dataset is built only from checked raw archives, the checked session calendar, the frozen `universes/nifty100_v0_20.csv`, and the saved full-window corporate-action endpoint rows. The builder must validate raw market data first, filter to the frozen 20 symbols, reject any unsupported corporate action for those symbols, require one valid ordinary-session bar per frozen symbol per research session, apply split/bonus backward-adjustment factors, and write a deterministic local CSV under `data/processed/`.

The processed CSV remains untracked because it is derived data. Each successful build must commit a manifest under `docs/validation/` containing the dataset version, row counts, source-format counts, applied corporate actions, per-symbol row counts, and a SHA-256 hash of the local processed CSV.

ISIN continuity may be explained by an identifier-changing corporate action on either the action ex-date or record date. The first processed build exposed a real selected-universe case: BAJAJFINSV has split and bonus records with ex-date `2022-09-13` and record date `2022-09-14`, while the market-data ISIN transition appears on `2022-09-14`.

**Evidence:** `docs/validation/PROCESSED_DATASET_V0.md` records the first frozen-universe processed build: 20 symbols, 2,618 ordinary full-window sessions, 52,360 processed bars, 0 market-data missing files, 0 file-level parser failures, 0 row-level rejections, 362 selected-symbol corporate actions, 14 supported split/bonus adjustments, and processed CSV SHA-256 `74f25a13116f5658201870ee6ae7c35ac5d27153ccbf3b65909e078355f75b4e`.

**Reason:** Backtests need one canonical adjusted OHLCV input instead of re-implementing validation, filtering, and adjustment logic inside strategy code. Keeping the large derived CSV out of git while committing a manifest preserves reproducibility without storing generated data in version control. The BAJAJFINSV record-date finding prevents a real split/bonus event from being falsely treated as a missing corporate action.

**Affected experiments:** Processed dataset construction, B001, B001-S015, B002, B002-S015, B003, B003-S015, benchmark comparison, and all downstream Phase 1 reports.

**Rerun required:** No strategy run exists yet.

---

## D-040 — Official Nifty 100 TRI benchmark source

**Date:** 24 August 2026
**Status:** Accepted

**Old rule:** Phase 1 named the Nifty 100 Total Return Index as the benchmark, but there was no implemented source contract, parser, or date-coverage validation for the benchmark series.

**New rule:** V0 uses the official NSE Indices historical-data report `Total returns Index Values` for `NIFTY 100`. Raw benchmark endpoint responses are local data under `data/raw/benchmarks/`, processed benchmark CSVs are local derived data under `data/processed/benchmarks/`, and neither is tracked. The committed artifact must be a validation report under `docs/validation/` with source, row counts, missing dates, extra dates, and interpretation.

Benchmark rows must have one index name, unique dates, positive TRI values, and one row for every ordinary research-bar session in the checked calendar. Missing benchmark dates are blocking. Extra dates are reported but are not blocking by themselves because D-029 excludes special sessions from V0 research bars.

If the official TRI series cannot be retrieved for an engineering run, any fallback must remain labelled as approximate under the existing Phase 0/Phase 1 fallback language and must not be used to approve or reject a strategy for paper/live promotion.

**Evidence:** `docs/validation/NIFTY100_TRI_BENCHMARK_SOURCE_V0.md` records the source contract. The first automation-environment fetch attempt reached NSE Indices but returned the historical-data HTML page rather than the JSON TRI payload, so no benchmark rows or validation artifact were committed from that response.

**Reason:** Benchmark handling must be frozen before B001 so the comparison period, dividend treatment, and date-alignment rules are not chosen after strategy results exist. The official TRI includes dividend effects and reinvestment, matching the Phase 0 benchmark requirement.

**Affected experiments:** Benchmark ingestion, B001, B001-S015, B002, B002-S015, B003, B003-S015, reporting, and all Phase 1 benchmark-relative drawdown checks.

**Rerun required:** No strategy run exists yet.

---

## D-041 — Nifty 100 TRI fetch and 2024 special-session calendar correction

**Date:** 24 August 2026
**Status:** Accepted

**Old rule:** D-040 registered the official NSE Indices `Total returns Index Values`
report for `NIFTY 100`, but the first implementation used the obsolete
`/Backpage.aspx/getTotalReturnIndexString` endpoint and received HTML instead
of TRI rows. The full-window NSE CM calendar also contained 13 explicit special
sessions and omitted three 2024 Saturday sessions later exposed by the official
benchmark series.

**New rule:** V0 fetches the official Nifty 100 TRI rows from
`/BackPage/getTotalReturnIndexString` using the page's `cinfo` JSON payload.
The parser accepts the live direct JSON row list and the older wrapped `d`
payload shape. `NTR_Value` may be `-` and is treated as unavailable, while
`TotalReturnsIndex` remains mandatory and positive.

The V0 session calendar adds 2024-01-20, 2024-03-02, and 2024-05-18 as explicit
`SPECIAL` sessions. They are kept for raw-file auditing and benchmark
date-alignment evidence but remain excluded from default research bars under
D-029. These three pre-transition special sessions use CM-UDiFF archives,
because the legacy CM bhavcopy archive URLs return HTML for those dates while
the CM-UDiFF ZIP archives exist and validate.

**Evidence:** The official Nifty 100 TRI fetch for 2016-01-01 through
2026-08-19 returned 2,634 benchmark rows with zero missing ordinary research
sessions and 16 extra dates. The extra dates are the 16 special sessions now
recorded in the full-window calendar. UDiFF archive probes for 2024-01-20,
2024-03-02, and 2024-05-18 returned ZIP archives; the corresponding legacy
URLs returned HTML.

**Reason:** Benchmark rows are an independent source of session evidence. Once
they exposed special sessions missing from the raw-data calendar, keeping the
old 13-session calendar would make acquisition auditing incomplete. Adding the
sessions does not change B001/B002/B003 research bars because special sessions
remain excluded by default, but it does preserve raw archive completeness and
prevents official benchmark rows from being mislabelled as unexplained extras.

**Affected experiments:** Session calendar, raw market-data acquisition,
benchmark ingestion, processed dataset construction, B001, B001-S015, B002,
B002-S015, B003, B003-S015, reporting, and all Phase 1 benchmark-relative
checks.

**Rerun required:** Rerun raw market-data acquisition and validation artifacts
for the corrected calendar. The processed V0 dataset hash is not expected to
change because ordinary research sessions are unchanged and special sessions
are excluded by default. No strategy run exists yet.

---

## D-042 — Backtest accounting core uses Decimal cash and explicit fills

**Date:** 24 August 2026
**Status:** Accepted

**Old rule:** Phase 1 required cash and holdings accounting plus a daily NAV
invariant, but the backtest package still contained only scaffolding and no
implemented accounting boundary.

**New rule:** The first backtest-core slice introduces only processed-dataset
bar access and portfolio accounting primitives. Processed bars are read from
the already built adjusted OHLCV CSV and exposed as deterministic daily symbol
lookups. Portfolio state is immutable, cash is quantized to paise using
`Decimal` and `ROUND_HALF_UP`, fills are explicit events with deterministic
ordering by `(trade_date, sequence, symbol, side)`, and mark-to-market NAV must
equal `cash + holdings_value` exactly after paise quantization.

The slice deliberately does not implement strategy rules, benchmark comparison,
cost aggregation, slippage, reporting, or a day-loop engine. It rejects binary
float prices/fees at the fill boundary, rejects buys that would create negative
cash, rejects sells above held quantity, and halts valuation when a held symbol
has no close.

**Evidence:** New tests cover processed-bar loading/grouping, duplicate
symbol-date rejection, positive adjusted prices, buy/sell accounting, exact NAV
invariant, binary-float rejection, negative-cash rejection, short-sell
rejection, deterministic fill ordering, and missing-close halt.

**Reason:** The accounting primitive should be proven independently before B001
or any strategy logic can hide errors inside a long backtest. Keeping fills
explicit and deterministic gives the later day-loop engine a narrow surface for
T+1 execution, cost application, and manual three-trade reconciliation.

**Affected experiments:** Backtest engine, portfolio accounting, B001,
B001-S015, B002, B002-S015, B003, B003-S015, reporting, and all Phase 1 NAV
checks.

**Rerun required:** No strategy run exists yet.

---

## D-043 — Backtest day loop applies explicit fills before daily valuation

**Date:** 26 August 2026
**Status:** Accepted

**Old rule:** D-042 introduced processed-bar access and portfolio accounting
primitives, but there was still no explicit day loop connecting daily bars,
scheduled fills, and daily NAV snapshots.

**New rule:** The first day-loop engine is deliberately minimal. It accepts
already grouped `DailyBars`, a starting `PortfolioState`, and pre-scheduled
explicit `PortfolioFill` objects. For each trading date, it applies fills
scheduled for that date through `PortfolioState`, then marks the portfolio to
market using that day's adjusted close values, and records one daily
`PortfolioSnapshot`.

The engine sorts daily bars by date, rejects duplicate day entries, rejects
fills scheduled for dates absent from the supplied daily-bar series, and relies
on portfolio accounting to halt if a held symbol has no valuation close. It
does not implement signals, rankings, slippage, costs, benchmark comparison,
turnover checks, reporting, or strategy-specific execution rules.

**Evidence:** New tests cover out-of-order daily input, scheduled buy and sell
fills, daily NAV snapshots, rejection of fills on non-session dates, duplicate
day rejection, and the missing-close valuation halt.

**Reason:** A small explicit day loop proves the accounting pipeline can move
through time before strategy code is introduced. Keeping fills pre-scheduled
prevents the first engine slice from mixing portfolio accounting with B001
signal generation or T+1 order construction.

**Affected experiments:** Backtest engine, portfolio accounting, B001,
B001-S015, B002, B002-S015, B003, B003-S015, reporting, and all Phase 1 NAV
checks.

**Rerun required:** No strategy run exists yet.

---

## D-044 — Execution adapter applies adverse slippage before cost allocation

**Date:** 26 August 2026
**Status:** Accepted

**Old rule:** D-043 allowed the day-loop engine to consume explicit
`PortfolioFill` objects, but there was no backtest boundary for turning
requested executions into slippage-adjusted fills with broker charges.

**New rule:** Requested executions are represented as explicit
`ExecutionFillRequest` rows with trade date, sequence, symbol, side, quantity,
and reference price. The execution adapter applies deterministic adverse
slippage to the reference price first: buys execute at
`reference_price * (1 + slippage_rate)` and sells execute at
`reference_price * (1 - slippage_rate)`, rounded to paise. It then passes the
slipped fills to the existing India delivery cost engine, using the daily cost
total as authoritative and the existing per-fill allocations as reporting and
portfolio-fee allocations.

The adapter is intentionally not a strategy engine. It does not generate
signals, size orders, compare benchmarks, enforce turnover limits, or write
reports. Slippage rates must be explicit decimal-safe values, and binary floats
remain rejected at the boundary.

**Evidence:** New tests cover adverse buy/sell slippage direction, deterministic
fill ordering, daily cost grouping, allocated fees summing back to the
authoritative daily cost total, compatibility with the day-loop engine, and
invalid slippage/reference-price rejection.

**Reason:** Phase 1 needs cost-aware explicit fills before B001 can run, but
strategy logic should not be mixed into the cost boundary. Applying slippage
before fee calculation matches the executed-turnover basis used by the cost
engine, while keeping all broker fee arithmetic in one module.

**Affected experiments:** Backtest execution, portfolio accounting, B001,
B001-S015, B002, B002-S015, B003, B003-S015, reporting, and all Phase 1
cost-drag checks.

**Rerun required:** No strategy run exists yet.

---

## D-045 — Weekly momentum signals are ranked mechanically before execution

**Date:** 26 August 2026
**Status:** Accepted

**Old rule:** The experiment ledger pre-registered 60-session weekly relative
momentum for B001/B002/B003, but the repository still had no strategy signal
boundary. Ranking, rebalance dates, execution, and portfolio accounting were
not separated in code.

**New rule:** The first strategy slice produces only weekly ranking signals.
For each supplied ordinary-session bar series, the signal date is the final
session in each ISO week. A symbol's score is:

```text
adjusted_close_on_signal_date / adjusted_close_60_sessions_earlier - 1
```

Symbols missing either the current close or the exact lookback-session close
are ineligible for that signal date. Scores rank by descending momentum, with
alphabetical symbol as the deterministic tie-break. The output is the desired
symbol list and full ranked score table for each signal date.

This slice does not create orders, size positions, apply execution costs, run a
portfolio, compare benchmarks, enforce turnover gates, or report B001 results.

**Evidence:** New tests cover final-session-of-week signal dates, exact
lookback-session scoring, missing-symbol ineligibility, alphabetical tie-breaks,
input validation, and duplicate daily-date rejection.

**Reason:** Strategy ranking should be auditable before order construction and
execution costs are connected. Keeping the ranking layer pure prevents B001
results from hiding errors in signal-date selection or momentum arithmetic.

**Affected experiments:** B001, B001-S015, B002, B002-S015, B003, B003-S015,
backtest execution, reporting, and all Phase 1 strategy diagnostics.

**Rerun required:** No strategy run exists yet.

---

## D-046 — Rebalance planner emits exits before entry intents

**Date:** 26 August 2026
**Status:** Accepted

**Old rule:** D-045 produced desired ranked symbols, but there was still no
boundary that compared those desired symbols with current holdings. The next
step toward B001 execution could have mixed signal ranking, rebalance changes,
position sizing, prices, costs, and portfolio accounting.

**New rule:** The rebalance planner is a symbol-level transition layer only. It
takes a signal date, current `PortfolioState`, and desired symbols from the
signal layer. It emits deterministic planned rebalance orders:

- held symbols absent from the desired list become full-quantity SELL exits;
- desired symbols already held produce no order;
- desired symbols not currently held become BUY entry intents with no share
  quantity yet;
- exit orders always sequence before entry intents;
- exits are sorted alphabetically by symbol;
- entries preserve the desired-symbol order from the signal layer.

Entry share quantity is intentionally unresolved in this slice because sizing
requires cash, prices, execution-date bars, and cost/slippage assumptions. This
planner does not create executable fills, apply prices, apply costs, run a
portfolio, compare benchmarks, enforce turnover gates, or report B001 results.

**Evidence:** New tests cover exit-before-entry ordering, full-quantity exits,
held desired symbols producing no order, entry order preserving signal rank,
empty desired lists exiting all holdings, duplicate desired-symbol rejection,
and signal-date validation.

**Reason:** The transition from signal output to portfolio changes should be
auditable before sizing and execution are introduced. Splitting this boundary
keeps B001 order construction from hiding whether changes came from ranking,
rebalance comparison, share sizing, or execution-cost assumptions.

**Affected experiments:** B001, B001-S015, B002, B002-S015, B003, B003-S015,
backtest execution, reporting, and all Phase 1 trade-log diagnostics.

**Rerun required:** No strategy run exists yet.

---

## D-047 — Rebalance sizing uses next-session opens and affordability checks

**Date:** 31 August 2026
**Status:** Accepted

**Old rule:** D-046 created deterministic exit orders and entry intents, but
entry share quantities were intentionally unresolved. A later layer still had
to apply execution-date prices, slippage, transaction costs, cash constraints,
and max-position constraints without mixing those decisions into signal ranking
or rebalance planning.

**New rule:** The order-sizing layer takes a `RebalancePlan`, the current
`PortfolioState`, execution-date `DailyBars`, and a pre-registered
`max_positions` value. Execution bars must be strictly after the signal date.
Desired symbols must not exceed `max_positions`.

Sizing creates executable fill requests as follows:

- exit orders use the full planned quantity and the execution-date adjusted
  open as the reference price;
- exits remain sequenced before entries;
- entry budget is capped by the smaller of available cash per new entry and
  reference NAV divided by desired position count;
- entry quantities are whole shares floored at the execution-date adjusted
  open;
- the existing execution-cost adapter applies the registered adverse slippage
  and cost model as the affordability check;
- if the resulting fills would make cash negative, entry quantities are reduced
  from the last entry backward until the full fill set is affordable;
- if even one share is unaffordable, the entry is skipped.

Missing execution bars halt sizing. This slice does not generate strategy
signals, choose rebalance dates, execute a full portfolio run, compare the
benchmark, enforce turnover gates, or report B001 results.

**Evidence:** New tests cover conversion from rebalance plans to executable fill
requests, full-quantity exits, entry sizing from next-session opens, gap/cost
resizing to avoid negative cash, unaffordable entry skips, max-position
rejection, same-day execution rejection, and missing execution-bar rejection.

**Reason:** Phase 1 requires that a close(T) signal create only an intent and
that final entry quantity be recomputed at the T+1 simulated fill price with
costs. Using the already-tested execution-cost adapter as the affordability
check avoids a second fee estimate while preserving the rule that the backtest
must never fund a gap-up entry with implicit leverage.

**Affected experiments:** B001, B001-S015, B002, B002-S015, B003, B003-S015,
backtest execution, reporting, and all Phase 1 trade-log diagnostics.

**Rerun required:** No strategy run exists yet.

---

## D-048 — Rebalance execution loop consumes precomputed desired symbols

**Date:** 31 August 2026
**Status:** Accepted

**Old rule:** The repository had separate layers for daily portfolio
accounting, costed execution fills, momentum ranking signals, rebalance plans,
and order sizing. There was still no small boundary proving that a close(T)
desired-symbol list executes on the next available session using the current
portfolio state.

**New rule:** The rebalance execution loop consumes daily bars plus a
precomputed mapping of signal date to desired symbols. For each ordinary
session, it executes the prior session's desired-symbol list at the current
session open by calling the existing rebalance planner, order sizer, and
execution-cost adapter, then marks NAV at that session's close.

Signals scheduled for dates absent from the daily bar series halt the loop.
Signals on the final supplied session are recorded as unexecuted because there
is no next-session open inside the supplied data. This slice does not generate
signals, choose universe members, run B001 on the frozen dataset, compare the
benchmark, enforce turnover gates, or produce final reports.

**Evidence:** New tests cover next-session execution timing, current-state use
for later rebalance plans, final-session unexecuted signals, unknown signal-date
rejection, duplicate daily-date rejection, and empty input rejection.

**Reason:** The backtest should connect the already-tested layers without
turning the first integrated step into a full strategy result. Keeping the loop
input as precomputed desired symbols makes the execution timing and accounting
boundary auditable before B001/B002/B003 are run.

**Affected experiments:** B001, B001-S015, B002, B002-S015, B003, B003-S015,
backtest execution, reporting, and all Phase 1 trade-log diagnostics.

**Rerun required:** No strategy run exists yet.

---

## D-049 — Round-trip turnover is evaluated after fills are produced

**Date:** 31 August 2026
**Status:** Accepted

**Old rule:** D-004 and D-007 fixed the research rule that turnover is measured
after the run, but the repository still had no code boundary that counted
completed round trips by calendar year from explicit fills.

**New rule:** V0 turnover evaluation is a post-run diagnostic over executed
long-only portfolio fills. It reconstructs open entry lots from BUY fills and
counts a completed round trip when a SELL closes an entry lot. Completed round
trips are grouped by the year of the exit fill.

Only caller-supplied complete calendar years are evaluated against the annual
limit. Partial years can still be reported, but they do not create PASS/FAIL
status and are not annualised. The evaluator reports every completed round trip,
including trades beyond the limit; it never blocks the 31st round trip during
execution.

This slice does not run B001, generate signals, choose a universe, compare the
benchmark, produce performance metrics, or write final reports.

**Evidence:** New tests cover annual completed-round-trip counts, complete-year
PASS/FAIL scope, reporting rather than blocking excess turnover, partial lot
closure, invalid sell rejection, and invalid limit/year inputs.

**Reason:** The turnover gate must be auditable before the first strategy run,
and the engine must not alter trading behaviour to satisfy the gate. Counting
from explicit fills keeps the limit separate from signal generation and order
execution.

**Affected experiments:** B001, B001-S015, B002, B002-S015, B003, B003-S015,
backtest execution, reporting, and all Phase 1 turnover diagnostics.

**Rerun required:** No strategy run exists yet.

---

## D-050 — Trade-log rows expose allocated fill-level costs

**Date:** 31 August 2026
**Status:** Accepted

**Old rule:** D-013 defined fill-level charges as reporting allocations that
must sum back to authoritative daily totals, and D-044 created costed execution
fills. The repository still had no reporting row that exposed each executed
fill with every allocated cost component itemised.

**New rule:** The trade-log reporting layer renders `ExecutionCostResult`
objects into immutable `TradeLogRow` records. Each row contains the executed
fill date, sequence, symbol, side, quantity, price, turnover, every allocated
cost component, total allocated cost, and the allocation note.

Trade-log rows are reporting views only. They do not replace the authoritative
daily cost totals and must retain the allocation note stating that the daily
total is authoritative.

This slice does not write CSV files, calculate performance metrics, compare
the benchmark, enforce turnover gates, run B001, or produce final reports.

**Evidence:** New tests cover itemised component rows, ordering across fills and
trade dates, empty executions, mismatch rejection, and component sums back to
the execution's authoritative daily cost totals.

**Reason:** Phase 1 requires itemised trade logs and at least one manual trade
reconciliation. Rendering rows directly from existing execution allocations
keeps reporting separate from accounting while making each fill auditable.

**Affected experiments:** B001, B001-S015, B002, B002-S015, B003, B003-S015,
reporting, manual reconciliation, and all Phase 1 trade-log diagnostics.

**Rerun required:** No strategy run exists yet.

---

## D-051 — Unfilled exits retry before replacement entries

**Date:** 31 August 2026
**Status:** Accepted

**Old rule:** D-012 required full exits to carry forward and retry when a held
symbol cannot execute, but the rebalance execution loop either executed a
planned order on the next session or halted during sizing when a tradeable
execution bar was unavailable.

**New rule:** The rebalance execution loop may receive an explicit set of
untradeable symbols by session. When a planned exit symbol is untradeable on
the execution session, the loop records the full exit as unfilled, leaves the
position untouched for same-day valuation, and retries the same desired-symbol
transition on the next supplied session.

Replacement entries from that same transition do not execute while any required
exit remains unfilled. If a new signal arrives while a prior exit is still
pending, the loop halts rather than choosing an undocumented priority rule.

This slice does not model intraday partial fills, circuit-limit mechanics,
missing valuation bars, stale-price reporting, full B001 execution, benchmark
comparison, or final reports.

**Evidence:** New tests cover unfilled full-exit retry, no stub holding after an
unfilled exit, replacement entries waiting until exits fill, unknown
untradeable-date rejection, and halting when a fresh signal arrives before a
pending exit is resolved.

**Reason:** Phase 1 requires that exits always target the full held quantity
and never become accidental stub exits. Separating explicit execution
untradeability from close-price valuation lets the backtester represent a
temporary no-fill condition without inventing leverage or selling part of a
position.

**Affected experiments:** B001, B001-S015, B002, B002-S015, B003, B003-S015,
backtest execution, manual reconciliation, reporting, and all Phase 1
trade-log diagnostics.

**Rerun required:** No strategy run exists yet.

---

## D-052 — Synthetic three-trade hand reconciliation before B001

**Date:** 31 August 2026
**Status:** Accepted

**Old rule:** Phase 1 required a mandatory three-trade hand test and at least
one manually reconciled trade, but the repository had only component-level
tests for sizing, execution costs, trade-log rows, day-loop snapshots,
unfilled-exit retry, and turnover counting.

**New rule:** Before B001 runs, the repository must contain a synthetic
three-trade reconciliation fixture that crosses those accounting layers in one
test. The fixture must hard-code the expected fills, itemised allocated costs,
cash balances, holdings values, final NAV, unfilled-exit retry behaviour,
affordability resizing, and completed round-trip count.

The synthetic fixture is an acceptance check for the backtest accounting path.
It does not replace the later real broker contract-note or funds-statement
reconciliation.

**Evidence:** `docs/validation/THREE_TRADE_HAND_RECONCILIATION_V0.md` records
the scenario and expected values. The new test executes three fills across a
five-session toy run: buy `AAA`, retry and complete a full `AAA` exit after one
unfilled session, then buy `BBB` after affordability resizing from 10 reference
shares to 9 executable shares. The final NAV is `1098.08`, total turnover is
`3073.16`, and the completed round-trip count is 1.

**Reason:** Phase 1 should prove cash, fees, holdings, NAV, trade-log
allocations, retry semantics, and turnover counting together before strategy
results exist. Keeping the fixture synthetic avoids using B001 data while still
making the arithmetic reviewable by hand.

**Affected experiments:** Backtest execution, portfolio accounting, reporting,
B001, B001-S015, B002, B002-S015, B003, B003-S015, and all Phase 1 manual
reconciliation checks.

**Rerun required:** No strategy run exists yet.

---

## D-053 — Performance metrics compare strategy NAV with aligned TRI

**Date:** 31 August 2026
**Status:** Accepted

**Old rule:** Phase 1 required net strategy results, Nifty 100 TRI comparison,
CAGR, volatility, maximum drawdown, and a benchmark-relative drawdown gate, but
the repository had no implemented reporting primitive for those metrics.

**New rule:** V0 performance metrics are calculated from daily strategy
portfolio snapshots and official Nifty 100 TRI rows aligned on the strategy
snapshot dates. Every strategy date must have a benchmark row. Extra benchmark
rows may be ignored by the metric primitive because benchmark coverage and
extra-date reporting are handled by the benchmark validation artifact.

CAGR uses calendar days between the first and final aligned observations, with
a 365-day year. Annualized volatility uses sample standard deviation of period
returns multiplied by `sqrt(252)`. Maximum drawdown is reported as a positive
magnitude from the daily close series. The benchmark-relative drawdown gate
passes when strategy maximum drawdown is no worse than benchmark maximum
drawdown over the identical aligned dates.

This slice does not write final reports, run B001/B002/B003, load processed
datasets, evaluate turnover gates, or decide whether any strategy passes Phase
1 overall.

**Evidence:** New tests cover aligned strategy NAV versus benchmark TRI,
ignoring extra benchmark rows, CAGR over a one-calendar-year period,
annualized volatility, maximum drawdown, drawdown gate PASS/FAIL, missing
benchmark-date rejection, duplicate-date rejection, empty input rejection, and
non-positive strategy NAV rejection.

**Reason:** Benchmark-relative metrics must be defined before B001 results
exist. Keeping the metric primitive small and date-aligned prevents later
reporting from comparing strategy and benchmark over subtly different periods.

**Affected experiments:** Reporting, benchmark comparison, B001, B001-S015,
B002, B002-S015, B003, B003-S015, and all Phase 1 benchmark-relative drawdown
checks.

**Rerun required:** No strategy run exists yet.

---

## D-054 — Phase 1 ledger references frozen V0 universe and dataset

**Date:** 31 August 2026
**Status:** Accepted

**Old rule:** The six Phase 1 experiment ledger rows were pre-registered with
placeholder values stating that the universe and research dataset were pending
freeze before execution.

**New rule:** After the V0 universe freeze and processed dataset build, all six
planned Phase 1 ledger rows reference the frozen universe version
`nifty100_v0_20_d037` and the processed dataset version
`nifty100_v0_adjusted_ohlcv_d039`.

The ledger result columns remain blank and every row remains `PLANNED`. This
change records already-frozen inputs only; it does not execute B001/B002/B003,
inspect strategy results, or update any result field.

**Evidence:** `docs/validation/NIFTY100_V0_UNIVERSE_FREEZE.md` records
selection rule version `nifty100_v0_20_d037`. `docs/validation/PROCESSED_DATASET_V0.md`
records dataset version `nifty100_v0_adjusted_ohlcv_d039`. New tests assert
that the six Phase 1 ledger rows contain those versions, contain no pending
universe/data placeholders, and still have blank result columns.

**Reason:** The ledger is the audit surface for pre-registered runs. Once the
universe and processed data are frozen, leaving placeholder values in the
ledger makes the run inputs ambiguous and weakens the record before B001.

**Affected experiments:** B001, B001-S015, B002, B002-S015, B003, B003-S015,
and all Phase 1 report/ledger artifacts.

**Rerun required:** No strategy run exists yet.

---

## D-055 — Phase 1 reports print frozen inputs, gates, and warnings

**Date:** 2 September 2026
**Status:** Accepted

**Old rule:** The repository could calculate aligned performance metrics,
turnover, execution costs, and trade-log rows, but it had no single report
artifact that rendered the required Phase 1 identity fields, benchmark-relative
drawdown gate, turnover gate, and research warnings.

**New rule:** V0 writes deterministic Markdown reports for Phase 1 experiment
summaries. The report must print the experiment ID, strategy name, universe
version, data version, aligned period, portfolio metrics, benchmark metrics,
relative CAGR/drawdown comparison, drawdown gate status, turnover gate status,
transaction costs, and the required research warnings.

This slice is a report writer only. It does not run B001/B002/B003, update the
experiment ledger result fields, write trade-log CSV files, calculate holding
period or win/loss diagnostics, or decide whether a strategy is eligible for
paper/live promotion.

**Evidence:** New tests cover the generated Markdown sections, frozen input
versions, portfolio and benchmark metric rendering, CAGR difference, drawdown
gate PASS/FAIL rendering, turnover gate rendering, transaction-cost totals,
default research warnings, and notes.

**Reason:** Final reports must be prepared before strategy results exist so
the warning labels and pass/fail surfaces are not chosen after seeing B001.
Keeping the writer small lets later runner code feed it already-computed
metrics without hiding new calculations in presentation code.

**Affected experiments:** Reporting, B001, B001-S015, B002, B002-S015, B003,
B003-S015, and all Phase 1 result artifacts.

**Rerun required:** No strategy run exists yet.

---

## D-056 — Phase 1 experiment runner is pure orchestration

**Date:** 3 September 2026
**Status:** Accepted

**Old rule:** The repository had separate components for weekly momentum
signals, rebalance execution, turnover counting, benchmark-relative performance
metrics, and Phase 1 report writing, but no single function that ran the
pre-registered weekly momentum flow end to end.

**New rule:** V0 adds a pure, input-driven Phase 1 experiment runner. The
runner accepts already-loaded daily bars, benchmark bars, universe symbols,
cash, max-position, slippage, and turnover-limit inputs. It generates weekly
momentum signals, runs the explicit rebalance loop, collects portfolio fills and
daily execution-cost results, evaluates completed round-trip turnover, and
summarizes aligned strategy NAV versus the Nifty 100 TRI benchmark.

This runner does not load files, download data, write reports, update the
experiment ledger, execute B001/B002/B003 against the frozen dataset, or
implement B003 hysteresis.

**Evidence:** New tests cover the runner wiring momentum signals into next-day
rebalance execution, collecting fills and costs, counting a completed round
trip, summarizing performance over aligned benchmark dates, preserving final
unexecuted signal dates, and rejecting invalid runner inputs.

**Reason:** Before running any Phase 1 experiment, the orchestration boundary
should be fixed and tested without hiding new calculations inside scripts or
reports. Keeping the runner free of file I/O makes later B001 execution
auditable and reproducible from explicitly supplied frozen inputs.

**Affected experiments:** B001, B001-S015, B002, B002-S015, B003, B003-S015,
and all Phase 1 result-generation scripts.

**Rerun required:** No strategy run exists yet.

---

## D-057 — Phase 1 run script writes artifacts but not ledger results

**Date:** 3 September 2026
**Status:** Accepted

**Old rule:** The pure Phase 1 runner could execute weekly momentum experiments
from supplied objects, but the repository had no command that loaded the frozen
processed dataset, frozen universe, and saved Nifty 100 TRI benchmark into that
runner.

**New rule:** V0 adds a small Phase 1 run script for supported B001/B002-style
weekly momentum experiments. The script reads frozen local input files, selects
either the research period or validation period from the ledger row, runs the
pure experiment runner, and writes a Markdown report plus allocated trade-log
CSV under the selected output directory.

The script does not update `experiments/ledger.csv`, commit result artifacts,
run validation automatically, or route B003 through the B001/B002 runner. B003
requires a separate hysteresis runner before it can be executed.

**Evidence:** New tests cover the script writing report and trade-log artifacts
from small local CSV fixtures, plus rejection of B003 before hysteresis support
exists. Benchmark and trade-log file helpers also have round-trip tests.

**Reason:** Executing a Phase 1 result should require an explicit command and
should leave the ledger untouched until the generated artifacts are reviewed.
Separating artifact generation from ledger mutation keeps the first B001 result
auditable and prevents accidental status/result edits during a dry run.

**Affected experiments:** B001, B001-S015, B002, B002-S015, B003, B003-S015,
and all Phase 1 result artifacts.

**Rerun required:** No strategy run exists yet.

---

## D-058 — B001 research-period result is rejected before validation

**Date:** 3 September 2026
**Status:** Accepted

**Old rule:** B001 was pre-registered and ready to run, but no strategy result
had been executed or recorded in the ledger.

**New rule:** The B001 baseline research-period run is permanently recorded
and marked `REJECTED` before inspecting the validation period. The run used the
frozen V0 universe, frozen processed dataset, Nifty 100 TRI benchmark, 2026
reference cost model, and baseline 0.05% adverse deterministic slippage.

Research-period result:

```text
Period: 2016-01-01 through 2022-12-30
Observations: 1726
Starting capital: 50000.00
Ending capital: 153653.80
Net return: 2.073076
CAGR: 0.173960
Maximum drawdown: 0.466630
Benchmark CAGR: 0.137013
Benchmark maximum drawdown: 0.379228
Completed round trips: 270
Transaction costs: 21705.52
Turnover gate: FAIL
Drawdown gate: FAIL
```

The validation period remains uninspected for B001. B003 remains the
pre-registered turnover-response candidate, but cannot be run until the
hysteresis runner exists.

**Evidence:** `experiments/results/B001_research/phase1_report.md` and
`experiments/results/B001_research/trade_log.csv` were generated by
`scripts/run_phase1_experiment.py --experiment-id B001 --period research`.
The experiment ledger records the research-period CAGR, max drawdown, turnover,
net return, `REJECTED` status, and a note that validation was not inspected.

**Reason:** The baseline violated the pre-registered annual turnover mandate
and had a worse maximum drawdown than the benchmark during the research period.
Because the research gates failed, the validation holdout should not be spent
on B001.

**Affected experiments:** B001 directly. B003 becomes the next eligible
pre-registered response once hysteresis execution is implemented.

**Rerun required:** No prior B001 result exists.

---

## D-059 — B003 hysteresis runner uses frozen entry and hold ranks

**Date:** 3 September 2026
**Status:** Accepted

**Old rule:** B003 was pre-registered as the turnover-response candidate after
B001, but the codebase only supported simple top-N weekly momentum signals.
The Phase 1 run script intentionally refused B003 because no hysteresis runner
existed yet.

**New rule:** V0 supports B003 as weekly momentum with deterministic
hysteresis. On each weekly signal date, the runner keeps previously desired
symbols while their current rank is 6 or better, exits symbols ranked below 6
or ineligible, and fills available slots only from symbols ranked 3 or better.
The maximum position count remains 3.

The implementation adds support only for the already pre-registered B003 and
B003-S015 parameter sets. It does not run either real experiment or inspect the
validation period.

**Evidence:** New tests cover the hysteresis signal rule holding a name that
falls from entry rank to hold rank, exiting once the hold rank is broken,
running the hysteresis experiment wrapper, and routing B003 through the Phase 1
run script.

**Reason:** B001 failed the research-period turnover gate, so B003 is the next
pre-registered response. The B003 execution path must exist and be tested
before any real B003 result is generated.

**Affected experiments:** B003 and B003-S015 directly. B001 remains rejected.

**Rerun required:** No B003 result exists yet.

---

## D-060 — B003 research-period result is rejected before validation

**Date:** 3 September 2026
**Status:** Accepted

**Old rule:** After B001 failed the research-period turnover gate, B003 was the
next pre-registered turnover-response candidate, but no B003 strategy result
had been executed or recorded.

**New rule:** The B003 research-period run is permanently recorded and marked
`REJECTED` before inspecting the validation period. The run used the frozen V0
universe, frozen processed dataset, Nifty 100 TRI benchmark, 2026 reference
cost model, baseline 0.05% adverse deterministic slippage, entry rank 3, hold
rank 6, and maximum 3 positions.

Research-period result:

```text
Period: 2016-01-01 through 2022-12-30
Observations: 1726
Starting capital: 50000.00
Ending capital: 122419.92
Net return: 1.448398
CAGR: 0.136461
Maximum drawdown: 0.512654
Benchmark CAGR: 0.137013
Benchmark maximum drawdown: 0.379228
Completed round trips: 124
Transaction costs: 10344.51
Turnover gate: PASS
Drawdown gate: FAIL
```

The validation period remains uninspected for B003. The hysteresis rule
reduced turnover materially versus B001, but did not pass the benchmark-relative
drawdown gate.

**Evidence:** `experiments/results/B003_research/phase1_report.md` and
`experiments/results/B003_research/trade_log.csv` were generated by
`scripts/run_phase1_experiment.py --experiment-id B003 --period research`.
The experiment ledger records the research-period CAGR, max drawdown, turnover,
net return, `REJECTED` status, and a note that validation was not inspected.

**Reason:** B003 was the pre-registered response to B001's excessive turnover.
It passed the turnover gate, but failed the research-period drawdown gate by
recording a worse maximum drawdown than the Nifty 100 TRI benchmark.

**Affected experiments:** B003 directly. B001 remains rejected. B001-S015,
B002, B002-S015, and B003-S015 remain unrun unless later selected under the
pre-registered protocol.

**Rerun required:** No prior B003 result exists.

---

## D-061 — B002 research-period result is rejected before validation

**Date:** 3 September 2026
**Status:** Accepted

**Old rule:** B002 was pre-registered as a separate 2-position
cost/concentration variant, but no B002 strategy result had been executed or
recorded.

**New rule:** The B002 research-period run is permanently recorded and marked
`REJECTED` before inspecting the validation period. The run used the frozen V0
universe, frozen processed dataset, Nifty 100 TRI benchmark, 2026 reference
cost model, baseline 0.05% adverse deterministic slippage, 60-session weekly
momentum, and maximum 2 positions.

Research-period result:

```text
Period: 2016-01-01 through 2022-12-30
Observations: 1726
Starting capital: 50000.00
Ending capital: 112085.33
Net return: 1.241707
CAGR: 0.122232
Maximum drawdown: 0.534276
Benchmark CAGR: 0.137013
Benchmark maximum drawdown: 0.379228
Completed round trips: 199
Transaction costs: 20937.49
Turnover gate: FAIL
Drawdown gate: FAIL
```

The validation period remains uninspected for B002. The 2-position variant
reduced completed round trips versus B001 but still violated the turnover gate
and had a worse drawdown than the benchmark.

**Evidence:** `experiments/results/B002_research/phase1_report.md` and
`experiments/results/B002_research/trade_log.csv` were generated by
`scripts/run_phase1_experiment.py --experiment-id B002 --period research`.
The experiment ledger records the research-period CAGR, max drawdown, turnover,
net return, `REJECTED` status, and a note that validation was not inspected.

**Reason:** B002 was a separately counted pre-registered trial. It failed both
research-period gates, so the validation holdout should not be spent on B002.

**Affected experiments:** B002 directly. B001 and B003 remain rejected.
B001-S015, B002-S015, and B003-S015 remain unrun unless later selected under
the pre-registered protocol.

**Rerun required:** No prior B002 result exists.

---

## D-062 — Phase 1 research runs stop before validation

**Date:** 3 September 2026
**Status:** Accepted

**Old rule:** B001, B002, and B003 were pre-registered Phase 1 research
configurations. B001, B002, and B003 had each been run on the research period
and recorded individually, but there was no consolidated stop decision.

**New rule:** Phase 1 strategy execution stops before validation because B001,
B002, and B003 were all rejected on research-period gates. The validation
period remains uninspected for these configurations.

The higher-slippage rows B001-S015, B002-S015, and B003-S015 remain unrun. They
are robustness rows, not rescue trials, and do not create a validation candidate
after the corresponding baseline research configurations have failed.

**Evidence:** `docs/validation/PHASE1_RESEARCH_REVIEW_V0.md` summarizes the
three completed research-period runs:

```text
B001: turnover gate FAIL, drawdown gate FAIL, status REJECTED
B002: turnover gate FAIL, drawdown gate FAIL, status REJECTED
B003: turnover gate PASS, drawdown gate FAIL, status REJECTED
```

**Reason:** The validation holdout should only be spent on a configuration that
passes the pre-registered research-period gates. None did. Continuing to
validation after research rejection would weaken the one-time holdout protocol.

**Affected experiments:** B001, B002, and B003 directly. B001-S015, B002-S015,
and B003-S015 remain unrun under the current protocol.

**Rerun required:** No.

---

## D-063 — Phase 2 begins with a locked B004 specification

**Date:** 3 September 2026
**Status:** Accepted

**Old rule:** Phase 1 was closed with no promoted strategy, and any next
candidate required a new experiment ID and pre-registration before execution.

**New rule:** Phase 2 starts with `docs/PHASE_2_RESEARCH_SPEC.md` as the
locked Stage 2.0 specification. `B004` is registered as the first Phase 2
baseline candidate, and `B004-S015` is registered as its higher-slippage
robustness row. Both are `PLANNED`; no Phase 2 strategy result exists yet.

Phase 2 has a hard cap of three baseline candidates: `B004`, `B005`, and
`B006`. `B004` consumes the first slot. The cap cannot be increased after
seeing Phase 2 results.

`B004` tests a weekly relative-momentum-with-hysteresis strategy with an
externally specified 200-session Nifty 100 TRI market-trend filter. The rule is
pre-registered before diagnosis, implementation, or execution:

```text
RISK_ON  if TRI(T) > SMA200(T)
RISK_OFF if TRI(T) <= SMA200(T)
```

No alternative SMA length, threshold, cadence, position count, entry rank, hold
rank, or slippage assumption may be previewed and substituted into `B004`.

`B004-S015` may run only if `B004` passes every baseline promotion gate. It is
not a rescue trial and does not authorize validation access.

**Evidence:** `docs/PHASE_2_RESEARCH_SPEC.md` records the Phase 2 boundary,
trial cap, B004 rules, B004-S015 robustness condition, promotion gates, and
holdout prohibition. `experiments/ledger.csv` records `B004` and `B004-S015` as
`PLANNED`.

**Reason:** Phase 1 rejected concentrated large-cap momentum before validation.
Phase 2 therefore needs a separate, externally motivated candidate with fixed
rules and a trial cap before any research-period strategy performance is
generated.

**Affected experiments:** `B004` and `B004-S015` directly. `B001`, `B002`, and
`B003` remain rejected. `B001-S015`, `B002-S015`, and `B003-S015` remain unrun
and are not rescue trials.

**Rerun required:** No. This decision registers planned Phase 2 work only; it
does not run a strategy.

---

## D-064 — Stage 2.1 diagnosis clears B004 for implementation

**Date:** 3 September 2026
**Status:** Accepted

**Old rule:** B004 was pre-registered as a planned Phase 2 candidate, but Stage
2.1 diagnosis had not yet been completed.

**New rule:** Stage 2.1 is complete. `docs/phase2/PHASE2_DIAGNOSIS_V0.md`
records a general-mechanism diagnosis and finds no fatal conceptual issue that
requires cancelling B004 before implementation.

The diagnosis does not run B004, does not simulate the regime filter, does not
inspect switch dates, does not identify worst Phase 1 episodes, does not test
alternative parameters, and does not inspect the validation holdout.

The next permitted stage is Stage 2.2 implementation of the frozen B004 rule,
followed by Stage 2.3 synthetic/unit validation. A real B004 research-period
run remains prohibited until those implementation and unit-validation steps are
complete.

**Evidence:** `docs/phase2/PHASE2_DIAGNOSIS_V0.md` records the Stage 2.1
boundary, external mechanism, implementation risks, fatal-problem check, and
Stage 2.2 requirements.

**Reason:** The B004 rule was fixed before diagnosis and has a plausible
external basis in long-term trend-following and documented momentum crash risk.
That is enough to proceed to implementation, but not enough to infer expected
performance.

**Affected experiments:** `B004` remains `PLANNED`. `B004-S015` remains
`PLANNED` and may run only if B004 passes every baseline promotion gate.

**Rerun required:** No. This decision records diagnosis only; it does not run a
strategy.

---

## D-065 — B004 implementation is ready for research-period execution

**Date:** 3 September 2026
**Status:** Accepted

**Old rule:** Stage 2.1 diagnosis cleared B004 for implementation, but the
frozen B004 rule was not yet implemented or covered by synthetic/unit tests.

**New rule:** Stage 2.2 implementation and Stage 2.3 synthetic/unit validation
are complete for B004. The implementation adds the externally specified
200-session Nifty 100 TRI regime filter, weekly-only filtered hysteresis
signals, warm-up cash/no-entry behavior, risk-off full-exit/no-entry behavior,
unfilled-exit retry behavior, regime reporting fields, return-concentration
metrics, and a runner block that prevents B004/B004-S015 validation-period
execution before Phase 3.

B004 remains `PLANNED`. No B004 real research-period run has been generated by
this decision. No B004-S015 robustness run has been generated. The validation
holdout remains sealed.

The next permitted step is a B004 run on the research period only:

```text
2016-01-01 through 2022-12-31
```

**Evidence:** `docs/phase2/B004_IMPLEMENTATION_STATUS_V0.md` records the
implementation scope, synthetic/unit validation coverage, and remaining
research boundary.

**Reason:** B004 can now be executed under its frozen specification without
adding new parameter choices or using validation-period strategy output.

**Affected experiments:** `B004` directly. `B004-S015` remains conditional and
may run only if B004 passes every baseline promotion gate.

**Rerun required:** No. This decision records implementation readiness only; it
does not run a strategy.

---

## D-066 — B004 research-period result is rejected before robustness

**Date:** 3 September 2026
**Status:** Accepted

**Old rule:** B004 was implemented and ready for a research-period-only run,
but no B004 result had been generated.

**New rule:** The B004 research-period run is permanently recorded and marked
`REJECTED` before robustness or validation. The run used the frozen Phase 2
specification, frozen V0 universe, frozen adjusted dataset, Nifty 100 TRI
benchmark, 2026 reference cost model, baseline 0.05% adverse deterministic
slippage, 60-session weekly momentum, B003 hysteresis thresholds, and the
externally specified 200-session Nifty 100 TRI trend filter.

Research-period result:

```text
Period: 2016-01-01 through 2022-12-30
Observations: 1726
Starting capital: 50000.00
Ending capital: 81332.15
Net return: 0.626643
CAGR: 0.071975
Maximum drawdown: 0.306676
Sharpe: 0.446175
Benchmark CAGR: 0.137013
Benchmark Sharpe: 0.837396
Benchmark maximum drawdown: 0.379228
Completed round trips: 127
Transaction costs: 7693.42
Maximum stock positive contribution share: 0.271728
Maximum calendar-year positive contribution share: 0.497509
Turnover gate: PASS
Drawdown gate: PASS
CAGR gate: FAIL
Sharpe gate: FAIL
Stock concentration gate: PASS
Calendar-year concentration gate: FAIL
```

B004-S015 is marked `NOT_RUN` because B004 failed frozen baseline promotion
gates. It is not a rescue trial.

**Evidence:** `experiments/results/B004_research/phase1_report.md`,
`experiments/results/B004_research/trade_log.csv`, and
`docs/phase2/B004_RESEARCH_REVIEW_V0.md`.

**Reason:** B004 improved drawdown versus the benchmark-relative threshold, but
it did not retain acceptable return, risk-adjusted performance, or
calendar-year diversification under the pre-registered gates. Since every gate
had to pass, B004 is rejected.

**Affected experiments:** B004 directly. B004-S015 remains unrun and is no
longer eligible under this baseline because B004 failed.

**Rerun required:** No prior B004 result exists.

---

## D-067 — Correct B004 stock-concentration calculation and report warning

**Date:** 4 September 2026
**Status:** Accepted

**Old rule:** The B004 report generated the stock-concentration statistic by
discarding losing completed trades before aggregating P&L by symbol. The
report also omitted the explicit `REGIME-SAMPLE LIMITATION` text required by
the Phase 2 specification, and its heading still said "Phase 1 Experiment
Report".

**New rule:** Stock concentration must match the frozen Phase 2 section 8.6
formula exactly: first aggregate total net realized completed-trade P&L for
each symbol, then clamp each symbol aggregate at zero before calculating the
maximum positive contribution share. Every report with B004-style regime
exposure must also state the required regime-sample limitation text.

The B004 research report was regenerated from the identical frozen
research-period run only to recompute deterministic report metrics under the
corrected formula. No B004 parameter, signal rule, execution rule, cost
assumption, gate, or status changed. No B004-S015 robustness run was generated.
No validation-period strategy output was generated or inspected.

Corrected B004 stock-concentration result:

```text
Maximum stock positive contribution share: 0.271728
Stock concentration gate: PASS
```

B004 remains `REJECTED` because CAGR, Sharpe, and calendar-year concentration
failed independently. The correction does not authorize reconsidering B004,
running B004-S015, tuning the SMA rule, or inspecting validation.

**Evidence:** `src/nse_quant/reporting/phase1_report.py`,
`tests/reporting/test_phase1_report.py`,
`experiments/results/B004_research/phase1_report.md`, and
`docs/phase2/B004_RESEARCH_REVIEW_V0.md`.

**Reason:** This is a preregistration-compliance correction to make the
implementation match the already-frozen formula. It is not a post-result
formula change or rescue trial.

**Affected experiments:** B004 report metrics only. B004-S015 remains
`NOT_RUN`.

**Rerun required:** Yes, report regeneration only. The deterministic B004
research-period run was regenerated from the same frozen inputs and rules to
replace the incorrect derived concentration value.

---

## D-068 — Promote concentration results to ledger fields before B005

**Date:** 4 September 2026
**Status:** Accepted

**Old rule:** `experiments/ledger.csv` recorded B004's CAGR, drawdown, Sharpe,
Sortino, Calmar, turnover, and net return as structured result fields, but its
stock-concentration and calendar-year-concentration values appeared only in
the B004 report, review artifact, and decision text.

**New rule:** The experiment ledger has explicit result fields for
`max_stock_positive_contribution_share` and
`max_calendar_year_positive_contribution_share`. B004 records the corrected
stock-concentration value `0.271728` and calendar-year concentration value
`0.497509`. Closed Phase 1 rows remain blank for these new fields because
their committed reports did not contain these Phase 2 concentration metrics.
Unrun robustness rows remain blank.

No strategy was rerun, no robustness run was generated, and no validation
output was inspected.

**Evidence:** `experiments/ledger.csv` and
`tests/test_experiment_ledger.py`.

**Reason:** B005/B006 pre-registration and review should read against a ledger
that carries Phase 2 concentration gates as structured fields, not only as
prose in review artifacts.

**Affected experiments:** B004 ledger result fields only.

**Rerun required:** No.

---

## D-069 — Pre-register B005 realized-volatility exposure scaling

**Date:** 4 September 2026
**Status:** Accepted

**Old rule:** After B004 was rejected, the next Phase 2 baseline slot was
available but no B005 mechanism, parameters, gates, or ledger rows had been
pre-registered.

**New rule:** B005 is pre-registered as Phase 2 baseline slot 2 of 3. It tests
a Barroso/Santa-Clara-style realized-volatility exposure overlay on the frozen
B003 weekly relative-momentum/hysteresis strategy. The realized-volatility
lookback is fixed at prior 6 months of daily momentum returns, adapted to 126
ordinary NSE sessions, and the target volatility is fixed at 12% annualized.

B005 is a long/cash, no-leverage repository adaptation:

```text
raw_multiplier = 0.12 / realized_volatility
exposure_multiplier = min(1.0, raw_multiplier)
```

The 100% cap is a project feasibility constraint because the current strategy
surface is cash-equity delivery-style long/cash exposure, not the original
self-financing long-short WML factor.

`B005-S015` is pre-registered as the only B005 robustness row and changes only
adverse deterministic slippage from 0.05% to 0.15%. It may run only if B005
passes every baseline research-period promotion gate.

No B005 implementation exists yet. No B005 research run exists yet. No
B005-S015 robustness run exists yet. No validation-period strategy output was
generated or inspected.

**Evidence:** `docs/validation/B005_PREREGISTRATION_V0.md`,
`experiments/ledger.csv`, `README.md`, and the B005 pre-registration tests.

**Reason:** B005 is externally motivated by published momentum risk-management
research and is materially different from B004's binary Nifty 100 TRI SMA200
trend filter. It freezes the relevant parameters before implementation or
execution, keeping the validation holdout sealed.

**Affected experiments:** B005 and B005-S015.

**Rerun required:** No.

---

## D-070 — Implement B005 realized-volatility exposure scaling

**Date:** 4 September 2026
**Status:** Accepted

**Old rule:** B005 was pre-registered but had no implementation, no report
support, and no runner path for research-period execution.

**New rule:** B005 implementation may be reviewed for research-period
execution. The implementation adds target-exposure-aware rebalance planning,
sizing, and execution; generates B005 weekly volatility-scaled hysteresis
momentum signals from the frozen B003 signal family; uses the pre-registered
126 ordinary-session realized-volatility lookback; uses the pre-registered
12% annualized target volatility; caps exposure at 1.0; and emits the required
B005 volatility-exposure report section and realized-volatility limitation
warning.

B005 and B005-S015 remain `PLANNED` in the ledger. No B005 real research-period
result was generated by this implementation branch. No B005-S015 robustness run
was generated. No validation-period strategy output was generated or inspected.

**Evidence:** `src/nse_quant/backtest/rebalance.py`,
`src/nse_quant/backtest/sizing.py`,
`src/nse_quant/backtest/rebalance_loop.py`,
`src/nse_quant/strategies/momentum.py`,
`src/nse_quant/experiments/phase1.py`,
`src/nse_quant/reporting/phase1_report.py`,
`scripts/run_phase1_experiment.py`,
`docs/phase2/B005_IMPLEMENTATION_STATUS_V0.md`, and the B005 implementation
tests.

**Reason:** B005 must be executable under the frozen pre-registration before a
single research-period run can be produced and reviewed. Separating the
implementation PR from the real B005 research run preserves a clean audit trail
and keeps validation sealed.

**Affected experiments:** B005 and B005-S015.

**Rerun required:** No.
