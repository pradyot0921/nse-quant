from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PHASE1 = ROOT / "docs" / "PHASE_1_VERTICAL_SLICE.md"
UNIVERSE_RULE = ROOT / "universes" / "selection_rule_v0.md"
CLOSEOUT = ROOT / "docs" / "validation" / "PHASE1_CLOSEOUT_STATUS_V0.md"
FINAL_CLOSEOUT = ROOT / "docs" / "validation" / "PHASE1_FINAL_CLOSEOUT_V0.md"
POSTMORTEM = ROOT / "docs" / "validation" / "PHASE1_RESEARCH_POSTMORTEM_V0.md"


def test_phase1_status_documents_reflect_research_stop():
    readme = " ".join(README.read_text(encoding="utf-8").split())
    phase1 = " ".join(PHASE1.read_text(encoding="utf-8").split())
    universe = " ".join(UNIVERSE_RULE.read_text(encoding="utf-8").split())
    closeout = " ".join(CLOSEOUT.read_text(encoding="utf-8").split())
    final_closeout = " ".join(FINAL_CLOSEOUT.read_text(encoding="utf-8").split())
    postmortem = " ".join(POSTMORTEM.read_text(encoding="utf-8").split())

    assert "B001/B002/B003 research cycle concluded with no strategy promoted" in readme
    assert "repo-owned closeout complete" in readme
    assert "VALIDATION HOLDOUT: uninspected" not in readme
    assert "Status:** IN PROGRESS" not in phase1
    assert "Last updated:** 19 August 2026" not in phase1
    assert "universe not frozen yet" not in universe
    assert "Frozen on 2026-08-24 as `nifty100_v0_20_d037`" in universe
    assert "| B001 research run | Rejected |" in closeout
    assert "| B002 research run | Rejected |" in closeout
    assert "| B003 research run | Rejected |" in closeout
    assert "| Validation holdout | Uninspected |" in closeout
    assert "| Phase 1 report statistics | Complete |" in closeout
    assert "| Formal Phase 1 closeout | Complete |" in closeout
    assert "Real Zerodha delivery cost reconciliation remains conditional" in closeout
    assert "gross/net P&L, slippage model, Sharpe, Sortino, Calmar" in closeout
    assert "no Phase 1 strategy candidate eligible for validation promotion" in closeout
    assert "| Strategy promoted from Phase 1 | No |" in final_closeout
    assert "| Repo-owned Phase 1 closeout | Complete |" in final_closeout
    assert "| Research postmortem | `docs/validation/PHASE1_RESEARCH_POSTMORTEM_V0.md` |" in final_closeout
    assert "The validation holdout remains sealed" in final_closeout
    assert "Do not run B001, B002, B003, B001-S015, B002-S015, or B003-S015" in final_closeout
    assert "Phase 1 found no promotable V0 strategy" in postmortem
    assert "positive trade-level statistics while still being a poor portfolio candidate" in postmortem
    assert "They are not rescue trials." in postmortem
    assert "validation holdout remains unspent" in postmortem
