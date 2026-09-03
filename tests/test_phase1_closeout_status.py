from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PHASE1 = ROOT / "docs" / "PHASE_1_VERTICAL_SLICE.md"
UNIVERSE_RULE = ROOT / "universes" / "selection_rule_v0.md"
CLOSEOUT = ROOT / "docs" / "validation" / "PHASE1_CLOSEOUT_STATUS_V0.md"


def test_phase1_status_documents_reflect_research_stop():
    readme = " ".join(README.read_text(encoding="utf-8").split())
    phase1 = " ".join(PHASE1.read_text(encoding="utf-8").split())
    universe = " ".join(UNIVERSE_RULE.read_text(encoding="utf-8").split())
    closeout = " ".join(CLOSEOUT.read_text(encoding="utf-8").split())

    assert "B001/B002/B003 research cycle concluded with no strategy promoted" in readme
    assert "VALIDATION HOLDOUT: uninspected" not in readme
    assert "Status:** IN PROGRESS" not in phase1
    assert "Last updated:** 19 August 2026" not in phase1
    assert "universe not frozen yet" not in universe
    assert "Frozen on 2026-08-24 as `nifty100_v0_20_d037`" in universe
    assert "| B001 research run | Rejected |" in closeout
    assert "| B002 research run | Rejected |" in closeout
    assert "| B003 research run | Rejected |" in closeout
    assert "| Validation holdout | Uninspected |" in closeout
    assert "no Phase 1 strategy candidate eligible for validation promotion" in closeout
