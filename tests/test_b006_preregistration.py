from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "docs" / "validation" / "B006_PREREGISTRATION_V0.md"
README = ROOT / "README.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"


def test_b006_preregistration_freezes_identity_and_boundaries():
    text = " ".join(PREREG.read_text(encoding="utf-8").split())

    assert "Status:** Pre-registered, not implemented, not run" in text
    assert "| Experiment ID | B006 |" in text
    assert "| Phase 2 baseline slot | 3 of 3 |" in text
    assert "Research period | 2016-01-01 through 2022-12-31" in text
    assert "Validation holdout | 2023-01-01 through 2026-08-19, sealed" in text
    assert "No B006 data build, implementation, or run should start until this pre-registration is merged" in text


def test_b006_preregistration_freezes_52_week_high_signal():
    text = " ".join(PREREG.read_text(encoding="utf-8").split())

    assert "George and Hwang" in text
    assert "https://doi.org/10.1111/j.1540-6261.2004.00695.x" in text
    assert "current adjusted close / highest adjusted close during the preceding 52 calendar weeks" in text
    assert "PH52(i,T)" in text
    assert "T - 364 calendar days <= d <= T" in text
    assert "Higher `PH52` is better" in text
    assert "Ties are broken alphabetically by symbol" in text


def test_b006_preregistration_records_warmup_and_caveats():
    text = " ".join(PREREG.read_text(encoding="utf-8").split())

    assert "`nifty100_v0_52w_high_input_warmup_d074`" in text
    assert "Warm-up purpose: signal construction only" in text
    assert "Performance start: 2016-01-01" in text
    assert "No B006 data build should begin until this pre-registration is merged" in text
    assert "https://ssrn.com/abstract=4587697" in text
    assert "supporting only" in text
    assert "https://ideas.repec.org/a/taf/apfiec/v21y2011i18p1369-1379.html" in text
    assert "52-WEEK-HIGH LIMITATION:" in text


def test_b006_preregistration_prohibits_rescue_variants():
    text = " ".join(PREREG.read_text(encoding="utf-8").split())

    assert "NO 26-week high" in text
    assert "NO 39-week high" in text
    assert "NO 2-year high" in text
    assert "NO combination with B003 momentum" in text
    assert "NO combination with B004 trend filter" in text
    assert "NO combination with B005 volatility scaling" in text
    assert "NO B006-S015 unless B006 baseline passes every gate" in text


def test_b006_preregistration_records_gates():
    text = " ".join(PREREG.read_text(encoding="utf-8").split())

    assert "strategy CAGR >= 0.137013" in text
    assert "strategy maximum drawdown <= 0.379228" in text
    assert "strategy Sharpe >= 0.837396" in text
    assert "completed round trips <= 30 in every complete calendar year" in text
    assert "maximum stock positive contribution share <= 0.30" in text
    assert "maximum calendar-year positive contribution share <= 0.35" in text
    assert "complete deterministic input-only 52-week warm-up" in text


def test_b006_status_is_visible_in_repo_status_documents():
    readme = " ".join(README.read_text(encoding="utf-8").split())
    decisions = " ".join(DECISIONS.read_text(encoding="utf-8").split())

    assert "Phase 2 after B006 warm-up data stop" in readme
    assert "B006 is cancelled before research execution" in readme
    assert "No B006 warm-up dataset was built" in readme
    assert "no B006 research result exists" in readme
    assert "D-074" in decisions
    assert "Pre-register B006 52-week-high proximity ranking" in decisions
