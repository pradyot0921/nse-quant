# Nifty 100 TRI Benchmark Source V0

**Status:** Source contract

## Source

Official source: `https://www.niftyindices.com/reports/historical-data`

Report: `Total returns Index Values`

Index: `NIFTY 100`

The Phase 1 benchmark remains the official Nifty 100 Total Return Index. The
loader targets the NSE Indices historical-data report rather than a third-party
copy. Raw endpoint responses are saved locally under `data/raw/benchmarks/` and
processed benchmark CSVs are written under `data/processed/benchmarks/`; both
are derived/local data and remain untracked.

## Validation Policy

Benchmark rows must parse as:

- one index name only;
- strictly positive Total Return Index values;
- optional strictly positive Net Total Return Index values;
- unique dates;
- one row for every ordinary research-bar session in the checked session
  calendar.

Missing benchmark dates are blocking because strategy NAV and benchmark
drawdown must be computed over the identical evaluation period. Extra benchmark
dates are reported but not blocking by themselves, because special sessions are
excluded from V0 research bars by D-029.

## Current Status

This commit adds the acquisition, parser, validation, CSV writer, and tests. The
full 2016-01-01 through 2026-08-19 benchmark fetch must be run before B001 and
must produce `docs/validation/NIFTY100_TRI_BENCHMARK_V0.md`.

The first fetch attempt from the current automation environment reached NSE
Indices but returned the historical-data HTML page rather than the JSON TRI
payload. No benchmark rows were committed from that response. The next step is
to run the same script from a browser-capable local session or update the
acquisition handshake until the official endpoint returns parseable TRI rows.
