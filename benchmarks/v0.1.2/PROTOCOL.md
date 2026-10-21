# v0.1.2 measurement protocol

This publication compares **current-kit v0.1.2 and direct Markdown reading**.
The recorded measurements were made on **2026-10-21**. Republishing this subset
and simplifying the runner did not create new model observations.

## Source identity and fixture

Every scenario's JSON contains SHA-256 hashes for the measured helper, rule
template and installer. These match this release's files; Git history and old
commit IDs are not required to identify the runtime. The kit template is 2,254
UTF-8 bytes; this byte count is not a token-saving percentage.

The fixture generator produces twelve fictional English project notes totaling
334,578 bytes (about 28 KB each), plus a 984-byte policy. Each project has current
decisions, 36 historical records and an essential release gate near the end.
Fixture hashes, exact prompts and answer oracles are available in the data and
[generator](../long_notes.py). No customer data is used.

| Scenario | Relevant projects | Direct baseline | Current kit |
|---|---|---|---|
| single-full | Lighthouse | Policy + complete note | Generated rule/helper |
| multi-full | Lighthouse, Orchard, Atlas | Policy + three complete notes | Same |
| multi-focused | Same three | Policy + Current decisions / Release gates only | Same |

Exact file paths and relevant headings are supplied to both methods. Nine
irrelevant project notes are present. This tests known-evidence extraction and
freshness, not discovery, semantic search, whole-history summaries, remote Git
sync, meeting transcription or editing. Actual deviations and recovery calls
remain in the counters; see the report's full-read caveat.

The two three-project scenarios have identical kit prompts/rules. Differences
between their kit totals reflect separate trials and cache/model variability,
not a change in the kit task.

## Four-turn session

Each client/method/repetition uses a fresh conversation, resumed across:

1. Initial current facts, compact JSON.
2. Repeat from conversation only; zero tools expected.
3. Substantive resumption with unchanged local files.
4. The same prompt after Lighthouse changes blue → teal, preserving length and
   nanosecond mtime. Full SHA-256 changes; all other notes must stay identical.

The published subset is three clients × three scenarios × two methods × two
repetitions × four turns = **144 turns in 36 sessions**. All trials of these two
methods are included, with formatting failures, extra reads and recovered
permission denials. No best-run selection or post-run case normalization.

## Original execution order and subset provenance

The original measurement batch also executed a third arm, whose results are
outside this current-version publication. Its positions are explicitly retained
as `omitted-arm` below and in JSON. They matter because provider caches were not
reset. The retained counters, answers, run records and evidence are unchanged.

| Scenario | Repetition 1 | Repetition 2 |
|---|---|---|
| single-full | direct → omitted-arm → kit | kit → omitted-arm → direct |
| multi-full | omitted-arm → kit → direct | direct → kit → omitted-arm |
| multi-focused | kit → direct → omitted-arm | omitted-arm → direct → kit |

Do not interpret the published subset as an isolated two-arm run. The current
runner below runs only the two published methods, in the same relative order.
It cannot recreate the historical cache state or guarantee the recorded totals.

- macOS 26.4, Apple Silicon, Python 3.10.5.
- Codex `0.163.0-alpha.10.2`: `gpt-6.1-sol`, medium effort.
- Claude Code `2.1.233`: `claude-opus-5`, medium; auxiliary-model tokens count.
- Cursor CLI `2026.10.19-6bbf2c4`: `composer-2.5`, default effort.
- Normal workspace/additional-directory trust and scoped tool permissions;
  no permission bypass, global configuration changes or real-vault access.
- Each client has a separate fixture/workspace. Arms for a client run sequentially;
  different clients may run concurrently.

## Accounting and evidence

Follow the [accounting definitions](../README.md#accounting). Primary total is
input including cached input once, plus output. Reduction is
`100 × (direct − kit) / direct`, using both sessions per client/scenario.
Positive means savings; negative means increased usage. Paired percentages
contain only two observations, not confidence intervals. Tool-body UTF-8 bytes
exclude wrappers and duplicate interleaved output; they are not model tokens.

Verify answers and helper status/hash evidence separately: every required file
initially present, all unchanged on turn 3, only Lighthouse CONTENT/new hash on
turn 4, no tools on the immediate follow-up. Unit tests additionally mutate an
omitted section with the same size/mtime, cover nested/fenced headings, and check
truncation, missing headings and unfiltered policy content in compact batches.

Provider caches were not flushed; startup context and hidden tool overhead were
not fully isolated. Compare methods within one client. No universal rate,
short-note threshold, Windows token saving or cost reduction follows from this.
Source hashes and raw-event fingerprints aid verification, but raw logs are not
publicly available. This limits independent inspection of the recorded sessions.

## Run a new comparison (consumes real model usage)

Use authenticated, compatible clients and Python 3.10+ on macOS. The helper and
installation guides support Windows, but this CLI benchmark's commands and
accounting were validated on macOS. Check client flags/counters if versions differ.
The current runner uses a frozen source checkout and an external output directory.

```sh
git clone --branch v0.1.2 https://github.com/UpHash-Network/obsidian-agent-kit.git ../oak-measured
python3 benchmarks/revision_tokens.py init --source ../oak-measured --dest ../local-token-runs
```

`init` creates only fictional files and records source hashes; it invokes no
models. Complete normal Cursor trust for `cursor/cursor` and `cursor/vault`
inside that destination. Run each client sequence after login and permissions:

```sh
python3 benchmarks/revision_tokens.py run-client --dest ../local-token-runs --client codex
python3 benchmarks/revision_tokens.py run-client --dest ../local-token-runs --client claude
python3 benchmarks/revision_tokens.py run-client --dest ../local-token-runs --client cursor
python3 benchmarks/aggregate_revision.py --source ../local-token-runs --output ../token-results
```

The runner preserves prompts, fixture and per-method rules, and records the new
run date and client versions. Missing usage, nonzero exits or altered fixtures
stop execution. Completed answers with recovered permission denials are retained,
not silently retried. Review exports before publishing; raw logs, machine paths,
account/session IDs and source workspaces stay local.
