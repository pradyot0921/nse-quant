"""Offline replay of the three-session TECHM March 2015 data-only fixture."""

from __future__ import annotations

import argparse
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path

from nse_quant.data.corporate_action_events import (
    METHODOLOGY_VERSION,
    adjust_ohlcv_events,
    parse_corporate_action_event,
)
from nse_quant.data.corporate_actions import CorporateActionRecord, OHLCVBar
from nse_quant.data.nse_legacy_acquisition import cm_bhavcopy_archive_url, cm_bhavcopy_raw_path
from nse_quant.data.nse_legacy_bhavcopy import parse_cm_bhavcopy_file


FIXTURE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "techm_2015_multi_action.json"


def validate(raw_root: Path, corporate_action_source: Path) -> dict[str, object]:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if fixture["methodology"] != METHODOLOGY_VERSION:
        raise ValueError("fixture methodology mismatch")
    source_bytes = corporate_action_source.read_bytes()
    if sha256(source_bytes).hexdigest() != fixture["corporate_action_source_sha256"]:
        raise ValueError("corporate-action source hash mismatch")
    action_row = fixture["corporate_action"]
    matching = [row for row in json.loads(source_bytes)
                if row.get("symbol") == "TECHM" and row.get("exDate") == "19-Mar-2015"
                and row.get("series") == "EQ"]
    if len(matching) != 1 or any(matching[0].get(key) != value for key, value in action_row.items()):
        raise ValueError("TECHM corporate-action row mismatch")
    source = CorporateActionRecord(
        symbol=action_row["symbol"], purpose=action_row["subject"],
        ex_date=datetime.strptime(action_row["exDate"], "%d-%b-%Y").date(),
        record_date=datetime.strptime(action_row["recDate"], "%d-%b-%Y").date(),
    )
    event = parse_corporate_action_event(source)
    bars = []
    archives = []
    for expected in fixture["bars"]:
        session = date.fromisoformat(expected["date"])
        path = cm_bhavcopy_raw_path(raw_root, session)
        digest = sha256(path.read_bytes()).hexdigest()
        if digest != expected["archive_sha256"]:
            raise ValueError(f"{session}: archive hash mismatch")
        parsed = parse_cm_bhavcopy_file(path)
        matches = [bar for bar in parsed.bars if bar.symbol == "TECHM"]
        if parsed.rejected_rows or parsed.trade_date != session or len(matches) != 1:
            raise ValueError(f"{session}: bhavcopy quality check failed")
        raw = matches[0]
        if raw.isin != expected["isin"]:
            raise ValueError(f"{session}: ISIN mismatch")
        for field in ("open", "high", "low", "close", "volume", "previous_close"):
            if Decimal(getattr(raw, field)) != Decimal(expected[field]):
                raise ValueError(f"{session}: {field} mismatch")
        bars.append(OHLCVBar(raw.symbol, raw.trade_date, raw.open, raw.high, raw.low,
                             raw.close, raw.volume, raw.isin))
        archives.append({"date": session.isoformat(), "url": cm_bhavcopy_archive_url(session),
                         "sha256": digest, "rejected_rows": 0})
    adjusted = adjust_ohlcv_events(bars, [event])
    if adjusted[0].price_factor != Decimal("0.25") or adjusted[0].volume_factor != Decimal("4"):
        raise ValueError("combined factors differ from the issuer's four-for-one share count")
    if any(bar.price_factor != 1 or bar.volume_factor != 1 for bar in adjusted[1:]):
        raise ValueError("ex-date or record-date bars were adjusted twice")
    return {
        "methodology": METHODOLOGY_VERSION,
        "status": "PASS",
        "scope": "TECHM 2015-03-18 through 2015-03-20 data-only; no strategy or holdout",
        "fixture_canonical_sha256": sha256(json.dumps(
            fixture, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")).hexdigest(),
        "corporate_action_source_sha256": fixture["corporate_action_source_sha256"],
        "issuer_source": fixture["issuer_source"],
        "components": [{"type": item.action_type.value,
                        "price_factor": str(item.price_adjustment_factor),
                        "volume_factor": str(item.volume_adjustment_factor)} for item in event.components],
        "archives": archives,
        "adjusted_bars": [{"date": item.bar_date.isoformat(), "isin": item.isin,
                           "raw_close": str(item.raw_close),
                           "adjusted_open": str(item.adjusted_open),
                           "adjusted_high": str(item.adjusted_high),
                           "adjusted_low": str(item.adjusted_low),
                           "adjusted_close": str(item.adjusted_close),
                           "raw_volume": str(item.raw_volume),
                           "adjusted_volume": str(item.adjusted_volume),
                           "price_factor": str(item.price_factor),
                           "volume_factor": str(item.volume_factor)} for item in adjusted],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--corporate-action-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args.raw_root, args.corporate_action_source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: TECHM multi-action source replay; report={args.output}")


if __name__ == "__main__":
    main()
