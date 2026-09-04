from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINDINGS = ROOT / "docs" / "phase2" / "PHASE2_INTERIM_FINDINGS_V0.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"


def test_phase2_interim_findings_records_risk_overlay_pattern():
    text = " ".join(FINDINGS.read_text(encoding="utf-8").split())

    assert "does not pre-register B006" in text
    assert "does not inspect the validation holdout" in text
    assert "| B003 | No Phase 2 overlay | 0.136461 | 0.512654 | 0.636888 | 124 |" in text
    assert "| B004 | Exogenous Nifty 100 TRI SMA200 regime filter | 0.071975 | 0.306676 | 0.446175 | 127 |" in text
    assert "| B005 | Realized-volatility exposure scaling | 0.032527 | 0.302637 | 0.332169 | 253 |" in text
    assert "continuous exposure resizing doubled completed round trips" in text
    assert "B006 should not spend the final baseline slot on another risk-control overlay" in text


def test_phase2_interim_findings_records_b003_beta_diagnostic():
    text = " ".join(FINDINGS.read_text(encoding="utf-8").split())

    assert "No separate daily B003 NAV CSV is committed" in text
    assert "| CAGR | 0.136461 | 0.136461 |" in text
    assert "| Maximum drawdown | 0.512654 | 0.512654 |" in text
    assert "| Sharpe | 0.636888 | 0.636888 |" in text
    assert "| Beta to Nifty 100 TRI | 1.016661 |" in text
    assert "| Annualized arithmetic alpha | 0.014954 |" in text
    assert "does not support the hypothesis that B003 was simply a concentrated 1.3-1.4 beta version" in text


def test_phase2_interim_finding_is_decision_logged():
    decisions = " ".join(DECISIONS.read_text(encoding="utf-8").split())

    assert "D-073" in decisions
    assert "Record Phase 2 interim risk-overlay and beta diagnostics before B006" in decisions
    assert "beta `1.016661`" in decisions
    assert "annualized arithmetic alpha `0.014954`" in decisions
