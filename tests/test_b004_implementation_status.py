from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "phase2" / "B004_IMPLEMENTATION_STATUS_V0.md"


def test_b004_implementation_status_records_no_real_run():
    text = " ".join(STATUS.read_text(encoding="utf-8").split())

    assert "Stage 2.2 implementation and Stage 2.3 synthetic/unit validation complete" in text
    assert "does not run B004 on the real research period" in text
    assert "does not inspect the validation holdout" in text
    assert "B004 remains `PLANNED`" in text
    assert "No validation-period strategy output may be generated" in text


def test_b004_implementation_status_records_required_unit_coverage():
    text = " ".join(STATUS.read_text(encoding="utf-8").split())

    assert "exactly 199 benchmark observations" in text
    assert "exactly 200 benchmark observations" in text
    assert "`TRI > SMA200`, risk-on" in text
    assert "`TRI == SMA200`, risk-off" in text
    assert "`TRI < SMA200`, risk-off" in text
    assert "unfilled risk-off exit is carried and retried" in text
    assert "direct B004-versus-B003 comparison reporting" in text
    assert "B004 validation-period runner execution is blocked" in text
