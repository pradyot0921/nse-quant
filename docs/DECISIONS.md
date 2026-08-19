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

**New rule:** NSE bonus ratios are interpreted as new shares per existing shares: `Bonus X:Y` means X new shares for Y held shares. Buyback records labelled `Buy Back` are `IGNORED` for price and volume adjustment because neither tender-offer buybacks nor open-market buybacks multiply or dilute the holdings of non-participating shareholders. V0 excludes any symbol with a rights issue inside the research window from the frozen universe unless a later decision adds deterministic rights adjustment support. During OHLCV validation, an ISIN change from the prior session with no same-date corporate-action record of any type must halt or quarantine the symbol/date as a possible missing corporate action.

**Evidence:** Official NSE CM-UDiFF bhavcopy checks:

- PATANJALI `Bonus 2:1`, ex-date 11 September 2025: prior close 1802.00, ex-date open 602.70. Correct convention predicts 600.67, a 0.34% difference; inverted convention predicts 901.00, a 33.11% difference.
- BEML face-value split 10 to 5, ex-date 3 November 2025: prior close 4399.80, ex-date open 2188.00. The 0.5 split factor predicts 2199.90, a 0.54% difference.
- INFY `Buy Back`, ex-date 14 November 2025: ten sessions either side showed ordinary market movement rather than a mechanical adjustment step. This corroborates, but does not replace, the structural no-entitlement-change reason for ignoring buybacks.
- BEML's ISIN changed across its split, showing that UDiFF row-level ISIN can independently reveal corporate-action continuity events.

**Reason:** The split and bonus price checks remove the final parser convention ambiguity using raw exchange bhavcopy data rather than unit-test assumptions. Buybacks do not create a share-count entitlement multiplier for shareholders who do not participate, so applying any automatic price/volume factor would be wrong. Rights issues do affect ex-date price continuity but are not supported in V0, so excluding affected symbols before the universe freeze prevents deadline pressure from weakening the quarantine gate. ISIN changes provide a cheap independent signal that can catch missing corporate-action records before adjusted OHLCV is trusted.

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
