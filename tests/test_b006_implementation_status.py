from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "phase2" / "B006_IMPLEMENTATION_STATUS_V0.md"
README = ROOT / "README.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"


def test_b006_implementation_status_records_ready_but_unrun_boundary():
    text = " ".join(STATUS.read_text(encoding="utf-8").split())

    assert "Superseded by B006 warm-up data stop" in text
    assert "implementation readiness for B006 as of D-075" in text
    assert "does not build the real B006 input-only warm-up dataset" in text
    assert "does not run B006 on the real research period" in text
    assert "does not inspect the validation holdout" in text
    assert "B006 is `CANCELLED`" in text
    assert "B006-S015 is `NOT_RUN`" in text


def test_b006_implementation_status_lists_required_mechanics():
    text = " ".join(STATUS.read_text(encoding="utf-8").split())

    assert "weekly 52-week-high proximity ranking signals" in text
    assert "T - 364 calendar days <= d <= T" in text
    assert "complete trailing warm-up enforcement" in text
    assert "missing adjusted-close rejection inside the required 52-calendar-week window" in text
    assert "unchanged B003-style hysteresis wrapper" in text
    assert "B006 validation-period runner block" in text
    assert "B006 actual research-period runner block" in text
    assert "mandatory 52-week-high limitation warning" in text


def test_b006_implementation_status_is_visible_in_repo_status_documents():
    readme = " ".join(README.read_text(encoding="utf-8").split())
    decisions = " ".join(DECISIONS.read_text(encoding="utf-8").split())

    assert "Phase 2 after B006 warm-up data stop" in readme
    assert "B006 is cancelled before research execution" in readme
    assert "D-075" in decisions
    assert "Implement B006 52-week-high proximity ranking" in decisions
    assert "No real B006 input-only warm-up dataset was built" in decisions
