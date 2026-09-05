# Phase 2 Final Closeout V0

**Status:** PHASE 2 COMPLETE - NO CANDIDATE PROMOTED

**Closeout date:** 2026-09-05

This artifact closes Phase 2 under Outcome B of the frozen research
specification. B004 and B005 failed their research-period gates. B006 was
cancelled after implementation, before dataset construction or research
execution. No candidate qualifies for Phase 3 validation.

This closeout uses existing committed artifacts only. It performs no strategy
run, NAV reconstruction, new diagnostic, or validation inspection.

## Final State And Trial Count

| Candidate | Baseline status | Reason | Robustness status |
| --- | --- | --- | --- |
| B004 | REJECTED | CAGR, Sharpe, and calendar-year concentration failed | B004-S015: NOT_RUN |
| B005 | REJECTED | CAGR, Sharpe, annual turnover, and calendar-year concentration failed | B005-S015: NOT_RUN |
| B006 | CANCELLED | Required 2015 warm-up contains unsupported corporate actions | B006-S015: NOT_RUN |

Phase 2 registered three baseline candidates and three conditional robustness
rows. Two baselines ran; one was cancelled after implementation; zero
robustness rows ran. Section 11 of the frozen specification counts candidates
that ran or were cancelled after implementation began. All three baseline
slots are therefore consumed. B006 is not a third performance rejection and
its cancellation does not create a replacement slot.

Across Phase 1 and Phase 2, five baseline research results were rejected
(B001-B005), and B006 has no research result. No strategy was promoted.

## Recorded Research Results

The research period was `2016-01-01 through 2022-12-31`; the reported ordinary
session series ends on `2022-12-30`. Values below are transcribed from the
committed reports and reviews, with return and drawdown expressed as decimals.

| Experiment | CAGR | Maximum drawdown | Sharpe | Completed round trips |
| --- | ---: | ---: | ---: | ---: |
| B003 reference | 0.136461 | 0.512654 | 0.636888 | 124 |
| B004 | 0.071975 | 0.306676 | 0.446175 | 127 |
| B005 | 0.032527 | 0.302637 | 0.332169 | 253 |
| Nifty 100 TRI benchmark | 0.137013 | 0.379228 | 0.837396 | N/A |

| Frozen gate | Threshold | B004 | B005 |
| --- | --- | --- | --- |
| Integrity violations | 0 | 0: PASS | 0: PASS |
| Maximum completed round trips in a complete year | <= 30 | 30: PASS | 51: FAIL |
| Maximum drawdown | <= 0.379228 | 0.306676: PASS | 0.302637: PASS |
| CAGR | >= 0.137013 | 0.071975: FAIL | 0.032527: FAIL |
| Sharpe | >= 0.837396 | 0.446175: FAIL | 0.332169: FAIL |
| Maximum stock positive contribution share | <= 0.30 | 0.271728: PASS | 0.263713: PASS |
| Maximum calendar-year positive contribution share | <= 0.35 | 0.497509: FAIL | 0.494308: FAIL |

Every gate had to pass. Passing drawdown and stock concentration did not
override the failed gates; neither baseline qualified for robustness.

## Findings And Limits

Both externally motivated overlays reduced drawdown to roughly 30% in this
sample, while more than halving B003's CAGR and lowering Sharpe. They did not
solve the combined return, risk, turnover, and concentration requirements in
the frozen 20-stock, three-position delivery-cost configuration.

B005's continuous exposure resizing accompanied 253 completed round trips,
versus 124 for B003, with five years above the annual turnover cap. The result
shows that lower exposure need not mean fewer transactions. These aggregate
comparisons do not isolate how much return was lost to costs, reduced
exposure, warm-up, or timing; no new attribution analysis is performed here.

The two overlays share an underlying engine and research window. Their
external motivations do not make these outcomes independent statistical
replications. This evidence does not establish that all risk overlays fail,
that momentum cannot work in India, or that a different ranking rule would
succeed. The project found no candidate that met its frozen promotion gates.

The existing B003 beta diagnostic in D-073 and the interim finding used a
deterministic NAV reconstruction because no separate daily B003 NAV CSV was
committed. It matched the committed report's aggregate metrics and recorded
1,725 daily return pairs, beta `1.016661`, and annualized arithmetic intercept
`0.014954` in a simple-return regression against Nifty 100 TRI.

That point estimate does not support the proposed 1.3-1.4 beta explanation.
The diagnostic does not report confidence intervals or significance tests,
and its arithmetic intercept is not excess CAGR or proof of a durable signal.
It cannot decide whether universe breadth or a different signal would work.

The mandatory regime-sample and noisy-realized-volatility limitations remain
in the B004 and B005 reports. Their limited sample and adaptation constraints
remain part of the research conclusion.

## B006 Data Stop And Audit History

B006 pre-registered 52-week-high proximity ranking with the existing 3/6
hysteresis wrapper. The first 2016 signal required history starting on
`2015-01-02`, mechanically determined by the 364-calendar-day lookback.

The warm-up scan found these unsupported selected-symbol records:

| Symbol | Ex-date | Event |
| --- | --- | --- |
| HCLTECH | 2015-03-19 | Bonus 1 : 1, an unsupported punctuation variant |
| TECHM | 2015-03-19 | Combined 1:1 bonus and face-value split from Rs 10 to Rs 5 |

TECHM's combined event is the blocking item under D-016's one-record/one-action
limitation. No B006 processed warm-up dataset was built. Its performance
fields remain blank and its 52-week-high hypothesis remains untested.

D-076, merged in PR #75 at `9158f4f4d19eafea5ab698ba2b38f4448fd489e9`, records
a sequencing discrepancy: PR #74 implemented B006 before this readiness
audit, although the frozen preregistration called for the check before
implementation. Cancellation occurred before real research execution. This
closeout retains that discrepancy rather than claiming full compliance with
the original sequence.

D-067 corrected B004's stock-concentration calculation to aggregate net
completed-trade P&L by symbol before clamping each aggregate at zero. The
corrected share is `0.271728`, replacing `0.181737`; D-068 put the corrected
value in the ledger. D-067 also restored the mandatory regime warning and
corrected the report title. B004's three independent gate failures remained.
These were corrections to the frozen definition's implementation and reporting,
not changes to its gates or a reconsideration of the rejection.

## Evidence Register

| Evidence | Artifact |
| --- | --- |
| Frozen Phase 2 rules, cap, and exit criteria | [Phase 2 specification](../PHASE_2_RESEARCH_SPEC.md) |
| Experiment states and recorded results | [Experiment ledger](../../experiments/ledger.csv) |
| Decisions D-067, D-068, D-073 through D-077 | [Decision log](../DECISIONS.md) |
| Initial diagnosis | [Phase 2 diagnosis](../phase2/PHASE2_DIAGNOSIS_V0.md) |
| Overlay comparison and B003 beta diagnostic | [Interim findings](../phase2/PHASE2_INTERIM_FINDINGS_V0.md) |
| B004 result and corrected gate review | [Report](../../experiments/results/B004_research/phase1_report.md), [review](../phase2/B004_RESEARCH_REVIEW_V0.md) |
| B005 frozen hypothesis | [Preregistration](B005_PREREGISTRATION_V0.md) |
| B005 result and gate review | [Report](../../experiments/results/B005_research/phase1_report.md), [review](../phase2/B005_RESEARCH_REVIEW_V0.md) |
| B003 reference result | [Report](../../experiments/results/B003_research/phase1_report.md) |
| B006 frozen hypothesis and data requirement | [Preregistration](B006_PREREGISTRATION_V0.md) |
| B006 implementation history | [Implementation status](../phase2/B006_IMPLEMENTATION_STATUS_V0.md) |
| B006 warm-up source scan | [Corporate-action scan](B006_CORPORATE_ACTION_WARMUP_SCAN_V0.md) |
| B006 cancellation and data blocker | [Input warm-up audit](B006_INPUT_WARMUP_DATASET_V0.md) |
| Phase 1 closure and data evidence chain | [Phase 1 final closeout](PHASE1_FINAL_CLOSEOUT_V0.md) |

Earlier preregistrations, reviews, and the interim finding retain their
historical next-step wording. This closeout and D-077 define the current
execution boundary.

## Holdout And Next Boundary

The validation holdout remains sealed:

```text
2023-01-01 through 2026-08-19
```

No baseline qualified for robustness, and no candidate is eligible for Phase
3. This closeout authorizes no strategy run, robustness run, validation
inspection, replacement Phase 2 candidate, or extension of the trial cap.

Any later research requires a separately approved, pre-registered cycle with
new experiment IDs and explicit data, trial-budget, and research gates. The
existing Phase 3 designation remains reserved for one-time validation of an
eligible candidate; it is not the next step for this closed cycle.

Real broker reconciliation remains a conditional external follow-up pending
suitable records. It does not change the research outcome. Any future work on
same-date multi-action corporate events needs its own deterministic data
methodology and tests before a fresh input dataset or strategy result.
