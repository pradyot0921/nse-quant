from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIAGNOSIS = ROOT / "docs" / "phase2" / "PHASE2_DIAGNOSIS_V0.md"


def test_phase2_diagnosis_closes_stage_without_results():
    text = " ".join(DIAGNOSIS.read_text(encoding="utf-8").split())

    assert "Stage 2.1 diagnosis complete" in text
    assert "does not run B004" in text
    assert "does not simulate a market-regime filter" in text
    assert "does not inspect regime switch dates" in text
    assert "does not inspect the validation holdout" in text
    assert "No fatal conceptual issue was found" in text
    assert "B004 remains:" in text
    assert "PLANNED" in text


def test_phase2_diagnosis_preserves_b004_guardrails():
    text = " ".join(DIAGNOSIS.read_text(encoding="utf-8").split())

    assert "No alternative SMA length, threshold, cadence, position count, or lookback" in text
    assert "strictly point-in-time" in text
    assert "weekly decision point" in text
    assert "cannot fabricate fills" in text
    assert "block validation-period strategy execution" in text
    assert "The validation holdout remains sealed" in text
