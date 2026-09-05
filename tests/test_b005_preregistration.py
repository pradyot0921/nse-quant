from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "docs" / "validation" / "B005_PREREGISTRATION_V0.md"
README = ROOT / "README.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"


def test_b005_preregistration_freezes_identity_and_boundaries():
    text = " ".join(PREREG.read_text(encoding="utf-8").split())

    assert "Status:** Pre-registered, not implemented, not run" in text
    assert "| Experiment ID | B005 |" in text
    assert "| Phase 2 baseline slot | 2 of 3 |" in text
    assert "Research period | 2016-01-01 through 2022-12-31" in text
    assert "Validation holdout | 2023-01-01 through 2026-08-19, sealed" in text
    assert "No B005 implementation or run should start until this pre-registration is merged" in text


def test_b005_preregistration_freezes_barroso_santa_clara_parameters():
    text = " ".join(PREREG.read_text(encoding="utf-8").split())

    assert "Barroso and Santa-Clara" in text
    assert "https://doi.org/10.1016/j.jfineco.2014.11.010" in text
    assert "Realized-volatility lookback: prior 6 months of daily returns" in text
    assert "Repository adaptation: 126 ordinary NSE sessions" in text
    assert "Target volatility: 12% annualized" in text
    assert "realized_vol(T) = sqrt((annualization_sessions / lookback_sessions)" in text
    assert "target_volatility = 0.12" in text
    assert "exposure_multiplier(T) = min(1.0, raw_multiplier(T))" in text
    assert "no leverage" in text


def test_b005_preregistration_distinguishes_b005_from_b004():
    text = " ".join(PREREG.read_text(encoding="utf-8").split())

    assert "B005 is not B004 with different trend-filter parameters" in text
    assert "binary market-regime switching" in text
    assert "continuous exposure scaling from trailing realized volatility" in text
    assert "not a momentum lookback, position-count, rebalance-frequency, slippage, or market-trend rescue trial" in text


def test_b005_preregistration_records_gates_and_limitation():
    text = " ".join(PREREG.read_text(encoding="utf-8").split())

    assert "strategy CAGR >= 0.137013" in text
    assert "strategy maximum drawdown <= 0.379228" in text
    assert "strategy Sharpe >= 0.837396" in text
    assert "maximum stock positive contribution share <= 0.30" in text
    assert "maximum calendar-year positive contribution share <= 0.35" in text
    assert "REALIZED-VOLATILITY LIMITATION:" in text
    assert "REALIZED VOLATILITY IS ITSELF NOISY" in text
    assert "DO NOT INTERPRET A GOOD RESULT AS PRECISE ESTIMATION" in text


def test_b005_status_is_visible_in_repo_status_documents():
    readme = " ".join(README.read_text(encoding="utf-8").split())
    decisions = " ".join(DECISIONS.read_text(encoding="utf-8").split())

    assert "B004 and B005 are rejected before robustness" in readme
    assert "B004-S015 and B005-S015 are not run" in readme
    assert "D-069" in decisions
    assert "Pre-register B005 realized-volatility exposure scaling" in decisions
    assert "D-070" in decisions
    assert "Implement B005 realized-volatility exposure scaling" in decisions
    assert "D-072" in decisions
    assert "B005 research-period result is rejected before robustness" in decisions
