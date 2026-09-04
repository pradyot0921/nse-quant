from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "phase2" / "B005_IMPLEMENTATION_STATUS_V0.md"


def test_b005_implementation_status_records_no_real_run():
    text = " ".join(STATUS.read_text(encoding="utf-8").split())

    assert "B005 implementation ready for research-period review" in text
    assert "does not run B005 on the real research period" in text
    assert "does not inspect the validation holdout" in text
    assert "B005 and B005-S015 remain `PLANNED`" in text
    assert "No validation-period strategy output may be generated" in text


def test_b005_implementation_status_records_required_unit_coverage():
    text = " ".join(STATUS.read_text(encoding="utf-8").split())

    assert "optional target exposure carrying through rebalance plans" in text
    assert "invalid target exposure rejection" in text
    assert "buy suppression while a required target-exposure sell-down is pending" in text
    assert "warm-up cash exposure until enough reference return observations exist" in text
    assert "realized-volatility calculation from prior squared daily reference returns" in text
    assert "exposure multiplier cap at 1.0" in text
    assert "B005 report exposure statistics and mandatory limitation warning" in text
    assert "B005 validation-period runner execution blocked" in text
