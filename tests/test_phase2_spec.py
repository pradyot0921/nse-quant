from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "PHASE_2_RESEARCH_SPEC.md"


def test_phase2_spec_freezes_governance_and_b004_before_execution():
    text = SPEC.read_text(encoding="utf-8")

    assert "**Status:** PRE-REGISTERED — NO PHASE 2 STRATEGY RUN YET" in text
    assert "**Validation holdout:** `2023-01-01..2026-08-19` — **SEALED**" in text
    assert "MAXIMUM BASELINE PHASE 2 CANDIDATES: 3" in text
    assert "5 September 2026, 23:59 Asia/Kolkata" in text

    assert "200-session SMA length" in text
    assert "RISK_ON  if TRI(T) > SMA200(T)" in text
    assert "RISK_OFF if TRI(T) <= SMA200(T)" in text
    assert "No alternative SMA length will be tested for B004." in text

    assert "strategy maximum drawdown <= 0.379228" in text
    assert "strategy CAGR >= 0.137013" in text
    assert "strategy Sharpe >= 0.837396" in text
    assert "maximum stock_positive_contribution_share <= 0.30" in text
    assert "maximum year_positive_contribution_share <= 0.35" in text

    assert "direct B004-versus-B003 comparison" in text
    assert "REGIME-SAMPLE LIMITATION:" in text
    assert "B004-S015" in text
    assert "Run `B004-S015` **only if B004 passes every baseline promotion gate**." in text


def test_phase2_diagnosis_prohibits_in_sample_drawdown_rule_design():
    text = SPEC.read_text(encoding="utf-8")

    prohibited = (
        "identify or rank the worst B001/B002/B003 dates, weeks, months, or episodes",
        "inspect which individual stocks caused the worst Phase 1 losses",
        "test alternative moving-average lengths",
        'run counterfactual "what would have avoided this drawdown?" analyses',
        "perform parameter sweeps, grids, optimization, or search",
        "inspect the validation holdout",
    )
    for item in prohibited:
        assert item in text
