from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE1 = ROOT / "docs" / "PHASE_1_VERTICAL_SLICE.md"
CLOSEOUT = ROOT / "docs" / "validation" / "PHASE1_CLOSEOUT_STATUS_V0.md"
VISUAL = ROOT / "docs" / "validation" / "CORPORATE_ACTION_VISUAL_VALIDATION_V0.md"
CHART = (
    ROOT
    / "docs"
    / "validation"
    / "assets"
    / "tcs_2018_bonus_visual_validation.svg"
)


def collapsed(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_corporate_action_visual_validation_artifact_is_recorded():
    visual = collapsed(VISUAL)

    assert "TCS" in visual
    assert "2018-05-31" in visual
    assert "Bonus 1:1 /Dividend- Rs 29 Per Share" in visual
    assert "Raw close ratio, ex-date / prior close | `0.4954469139`" in visual
    assert "Adjusted close ratio, ex-date / prior close | `0.9908938277`" in visual
    assert "The validation holdout was not inspected for strategy performance" in visual
    assert "does not promote any Phase 1 strategy" in visual


def test_corporate_action_visual_chart_exists_and_is_described():
    chart = collapsed(CHART)

    assert CHART.exists()
    assert "TCS 2018 bonus visual validation" in chart
    assert "Raw close shows the mechanical bonus adjustment drop" in chart
    assert "Adjusted close" in chart


def test_phase1_closeout_tracks_visual_validation_status():
    assert "- [x] One real event inspected visually." in PHASE1.read_text(encoding="utf-8")
