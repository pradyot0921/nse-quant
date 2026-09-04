from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "phase2" / "B005_RESEARCH_REVIEW_V0.md"
REPORT = ROOT / "experiments" / "results" / "B005_research" / "phase1_report.md"


def test_b005_research_review_records_rejection_without_robustness():
    text = " ".join(REVIEW.read_text(encoding="utf-8").split())

    assert "Rejected before robustness" in text
    assert "does not inspect the validation holdout" in text
    assert "does not run B005-S015" in text
    assert "| Maximum complete-year completed round trips | 51 | <= 30 | FAIL |" in text
    assert "| Maximum drawdown | 0.302637 | <= 0.379228 | PASS |" in text
    assert "| CAGR | 0.032527 | >= 0.137013 | FAIL |" in text
    assert "| Sharpe | 0.332169 | >= 0.837396 | FAIL |" in text
    assert "| Maximum stock positive contribution share | 0.263713 | <= 0.30 | PASS |" in text
    assert "| Maximum calendar-year positive contribution share | 0.494308 | <= 0.35 | FAIL |" in text
    assert "B005-S015 is not run" in text
    assert "B006 may not be B005 with a different volatility target" in text


def test_b005_research_report_contains_required_phase2_metrics():
    text = " ".join(REPORT.read_text(encoding="utf-8").split())

    assert "| Experiment | `B005` |" in text
    assert "## Annual Turnover Detail" in text
    assert "| 2017 | 51 | yes | FAIL |" in text
    assert "## Volatility Exposure" in text
    assert "| Realized-volatility lookback sessions | 126 |" in text
    assert "| Target volatility | 0.120000 |" in text
    assert "| Maximum exposure multiplier | 0.804678 |" in text
    assert "REALIZED-VOLATILITY LIMITATION:" in text
    assert "## Return Concentration" in text
    assert "| Maximum stock positive contribution share | 0.263713 |" in text
    assert "| Maximum calendar-year positive contribution share | 0.494308 |" in text
    assert "## Direct Candidate Comparison" in text
