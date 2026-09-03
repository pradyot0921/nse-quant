from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE2_SPEC = ROOT / "docs" / "PHASE_2_RESEARCH_SPEC.md"


def test_phase2_spec_locks_b004_before_any_run():
    spec = " ".join(PHASE2_SPEC.read_text(encoding="utf-8").split())

    assert "Status:** PRE-REGISTERED" in spec
    assert "NO PHASE 2 STRATEGY RUN YET" in spec
    assert "Validation holdout:** `2023-01-01..2026-08-19`" in spec
    assert "Phase 2 must not inspect strategy performance on the validation holdout" in spec
    assert "The immediate Phase 2 candidate is `B004`" in spec
    assert "No alternative SMA length will be tested for B004" in spec
    assert "MAXIMUM BASELINE PHASE 2 CANDIDATES: 3" in spec
    assert "B004-S015" in spec
    assert "Run `B004-S015` **only if B004 passes every baseline promotion gate**" in spec
    assert "Do **not** run B004 yet" in spec


def test_phase2_spec_records_exact_b004_gates():
    spec = " ".join(PHASE2_SPEC.read_text(encoding="utf-8").split())

    assert "strategy maximum drawdown <= 0.379228" in spec
    assert "strategy CAGR >= 0.137013" in spec
    assert "strategy Sharpe >= 0.837396" in spec
    assert "completed round trips <= 30" in spec
    assert "maximum stock_positive_contribution_share <= 0.30" in spec
    assert "maximum year_positive_contribution_share <= 0.35" in spec
    assert "A high CAGR cannot compensate" in spec
