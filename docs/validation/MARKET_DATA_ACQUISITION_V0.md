# Market Data Acquisition V0

## Scope

Downloads or reuses immutable raw NSE market-data archives for the
checked-in V0 session calendar. Existing archives are ZIP-validated before
reuse; corrupt existing archives are deleted and re-downloaded once by the
batch layer.

## Summary

| Metric | Count |
| --- | ---: |
| Records acquired or reused | 2631 |
| Missing archives | 0 |
| Failed archives | 0 |

## Source Counts

| Source | Count |
| --- | ---: |
| cm_udiff | 526 |
| legacy_cm_bhavcopy | 2105 |

## Status Counts

| Status | Count |
| --- | ---: |
| reused | 2631 |

## Missing Archives

None.

## Failed Archives

None.

## Interpretation

Missing or failed archives are data-quality problems that must be reviewed
before universe selection. This report records raw-file availability only;
row-level parser validation is performed separately by
`scripts/validate_market_data_window.py`.
