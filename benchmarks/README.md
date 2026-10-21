# Token measurements

[Current v0.1.2 report](v0.1.2/README.md) · [日本語](v0.1.2/README.ja.md) · [Protocol and reproduction](v0.1.2/PROTOCOL.md)

Only current-version results versus direct reading are published here. The
fixture contains twelve deterministic fictional project notes; real work data,
raw client logs, local paths and earlier-version results are excluded.

`revision_tokens.py` runs the two-method experiment. `long_notes.py` defines the
fixture, questions and direct-read instructions. `run_tokens.py` supplies the
client launcher and local evidence capture. `aggregate_tokens.py` normalizes
usage; `aggregate_long_notes.py` grades answers and summarizes tool actions;
`aggregate_revision.py` exports sanitized results with freshness checks.
Real-client runs are opt-in and consume model usage. Automated tests do not.

## Accounting

The primary total is client-reported input, including cached input counted once,
plus output. It is not billed cost, unique text size or subscription-quota use.

- **Codex:** cumulative counters across resume are differenced per turn. Cached
  input is already inside input; never add it twice. Final cumulative input plus
  output is the session total. Output includes reasoning; no independent
  cache-write component was observed in the published run.
- **Claude Code:** sum every model's `result.modelUsage` input, cache creation,
  cache read and output for each invocation, including auxiliary models.
- **Cursor:** sum each invocation's `result.usage` input, cache write, cache read
  and output. These are run-linked CLI counters, not dashboard time matching.

Missing counters are an error, never zero. Retain unfavorable trials, format
failures, recovery calls and completed permission-denial recoveries. Compare
within one client; provider counters do not make cross-client prices comparable.

Raw-event SHA-256 fingerprints can verify a locally retained log but do not make
that private log independently inspectable. Review sanitized exports before
publication. Keep personal paths, credentials, accounts and unrelated context local.
