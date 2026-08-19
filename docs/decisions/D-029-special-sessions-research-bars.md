# D-029 — Special sessions are audited but excluded from V0 research bars

**Date:** 20 August 2026  
**Status:** Proposed in PR #10

**Old rule:** The checked-in NSE CM session calendar distinguished `NORMAL` and `SPECIAL` sessions, but did not define whether special sessions should enter the research bar series used for lookbacks, signal generation, or simulated execution.

**New rule:** V0 keeps special sessions in the checked-in calendar for raw CM-UDiFF file auditing. A missing raw file for a special session is still a data-acquisition problem, and a raw file on an unlisted date is still a calendar mismatch. By default, research bar construction uses only `NORMAL` sessions. Special sessions enter a research run only through an explicit opt-in parameter and must be labelled in any resulting dataset/report.

**Evidence:** The 20-Aug-2025 to 19-Aug-2026 calendar contains two special sessions: 21 October 2025 Diwali Muhurat trading and 1 February 2026 Union Budget Sunday trading. The 21 October 2025 Muhurat CM-UDiFF file was inspected directly: it contains 2,291 `EQ` rows and uses `SsnId=F1`, the same session identifier observed in normal-session files. `SsnId` therefore cannot be relied on to identify special sessions; the checked-in calendar is the source of truth.

**Reason:** Muhurat and other special sessions have unusual timing, liquidity, and market context. Counting them as ordinary daily bars would let a short symbolic or otherwise abnormal session affect momentum lookbacks, rebalance observations, and next-session execution by omission. Keeping them in acquisition auditing preserves raw-data completeness while excluding them from default research avoids silently changing the meaning of a trading day.

**Affected experiments:** UDiFF loader, data validation, universe construction, B001/B002/B003, backtester, reporting, and all downstream Phase 1 backtests.

**Rerun required:** No market-data pipeline, universe, or strategy run has been frozen yet.

**Notes:** This entry is stored as a separate decision note in PR #10 because the current local shell cannot clone/read the private repository's full `docs/DECISIONS.md` safely for an append-only update. Before merging, fold this entry into `docs/DECISIONS.md` if the project keeps a single monolithic decision log.
