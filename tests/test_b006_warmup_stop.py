from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WARMUP = ROOT / "docs" / "validation" / "B006_INPUT_WARMUP_DATASET_V0.md"
SCAN = ROOT / "docs" / "validation" / "B006_CORPORATE_ACTION_WARMUP_SCAN_V0.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"


def test_b006_warmup_artifact_records_cancellation_before_research():
    text = " ".join(WARMUP.read_text(encoding="utf-8").split())

    assert "Blocked before dataset build; B006 cancelled before research execution" in text
    assert "not a B006 research result" in text
    assert "does not run B006" in text
    assert "does not run B006-S015" in text
    assert "does not inspect validation-period strategy output" in text
    assert "Do not build `data/processed/nifty100_v0_52w_high_input_warmup.csv`" in text


def test_b006_warmup_artifact_records_mechanical_window_and_blockers():
    text = " ".join(WARMUP.read_text(encoding="utf-8").split())

    assert "2016-01-01 - 364 calendar days = 2015-01-02" in text
    assert "2015-01-02 through 2015-12-31" in text
    assert "Performance start: 2016-01-01" not in text
    assert "| HCLTECH | 2015-03-19 | Bonus 1 : 1 | Unsupported punctuation variant |" in text
    assert "| TECHM | 2015-03-19 | Bonus 1:1 / Face Value Split - From Rs 10/- Per Share To Rs 5/- Per Share | Unsupported combined split-plus-bonus event |" in text
    assert "D-016 states that combined split-plus-bonus purpose strings are unsupported" in text
    assert "data-validity stop, not evidence for or against the 52-week-high ranking hypothesis" in text


def test_b006_corporate_action_warmup_scan_is_recorded():
    text = " ".join(SCAN.read_text(encoding="utf-8").split())

    assert "# B006 Corporate-Action Warm-Up Scan V0" in SCAN.read_text(encoding="utf-8")
    assert "Window: `2015-01-02` to `2015-12-31`" in text
    assert "Endpoint rows: `1911`" in text
    assert "EQ rows scanned: `1883`" in text
    assert "| UNSUPPORTED | 36 |" in text
    assert "Row-Level Failures None." in text
    assert "Bonus 1:1 / Face Value Split - From Rs 10/- Per Share To Rs 5/- Per Share" in text


def test_b006_warmup_stop_decision_is_recorded():
    text = " ".join(DECISIONS.read_text(encoding="utf-8").split())

    assert "D-076" in text
    assert "Cancel B006 before research execution after warm-up corporate-action audit" in text
    assert "B006 is cancelled before research execution" in text
    assert "TECHM 2015-03-19 Bonus 1:1 / Face Value Split" in text
    assert "Do not run B006" in text
    assert "Do not run B006-S015" in text
    assert "Do not inspect validation" in text
