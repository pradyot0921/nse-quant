from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "phase2" / "B004_RESEARCH_REVIEW_V0.md"
REPORT = ROOT / "experiments" / "results" / "B004_research" / "phase1_report.md"


def test_b004_research_review_records_rejection_without_robustness():
    text = " ".join(REVIEW.read_text(encoding="utf-8").split())

    assert "Rejected before robustness" in text
    assert "does not inspect the validation holdout" in text
    assert "does not run B004-S015" in text
    assert "| CAGR | 0.071975 | >= 0.137013 | FAIL |" in text
    assert "| Sharpe | 0.446175 | >= 0.837396 | FAIL |" in text
    assert "| Maximum stock positive contribution share | 0.271728 | <= 0.30 | PASS |" in text
    assert "| Maximum calendar-year positive contribution share | 0.497509 | <= 0.35 | FAIL |" in text
    assert "supersedes the originally reported `0.181737`" in text
    assert "B004-S015 is not run" in text
    assert "B005 may not be B004 with a different SMA length" in text


def test_b004_research_report_contains_required_phase2_metrics():
    text = " ".join(REPORT.read_text(encoding="utf-8").split())

    assert "| Experiment | `B004` |" in text
    assert "## Annual Turnover Detail" in text
    assert "| 2019 | 30 | yes | PASS |" in text
    assert "## Market Regime" in text
    assert "| Weekly regime state changes | 24 |" in text
    assert "REGIME-SAMPLE LIMITATION:" in text
    assert "THE SMA200 RULE IS EXOGENOUSLY SPECIFIED" in text
    assert "## Return Concentration" in text
    assert "| Maximum stock positive contribution share | 0.271728 |" in text
    assert "| Maximum calendar-year positive contribution share | 0.497509 |" in text
    assert "## Direct Candidate Comparison" in text
