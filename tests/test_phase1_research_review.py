from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "validation" / "PHASE1_RESEARCH_REVIEW_V0.md"


def test_phase1_research_review_records_stop_before_validation():
    text = REVIEW.read_text(encoding="utf-8")

    assert "`2023-01-01..2026-08-19` remains uninspected" in text
    assert "| B001 | 3-position weekly momentum | 0.173960 | 0.466630" in text
    assert "| B002 | 2-position weekly momentum | 0.122232 | 0.534276" in text
    assert "| B003 | 3-position weekly momentum with hysteresis | 0.136461 | 0.512654" in text
    assert "No Phase 1 strategy run qualifies for validation-period inspection." in text
    assert "B001-S015, B002-S015, and B003-S015 remain unrun" in text
