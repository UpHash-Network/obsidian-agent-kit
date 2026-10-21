# v0.1.2: token usage versus direct reading

[日本語](README.ja.md) · [Protocol / reproduce](PROTOCOL.md) · [All comparison data](summary.json) · [Compact reads](../../docs/compact-context.md)

**v0.1.2 used fewer tokens in 6 of 9 client/workload comparisons.** Best observed
reductions: Codex **53.2%** on three projects, Claude Code **48.0%** on one project,
and Cursor **40.7%** on three projects, all against full-read instructions.
These are each client's best of three workloads, using both repetitions—not
best runs, typical savings, billed costs or account-quota reductions.

Measured on **2026-10-21**, with twelve fictional English project notes of about
28 KB each. This repository publishes only the **direct-read/current-kit subset**
of that batch: **36 sessions, 144 turns**, two four-turn repetitions per client,
workload and method. Every trial of these two methods is retained. No model was
rerun for this republication. The original batch also included an omitted arm;
its positions remain in the data because provider caches were not reset.

## All current-version comparisons

Each total sums two four-turn sessions. Positive paired percentages mean
reductions, negative mean increases. Ranges contain two observations, not
confidence intervals. The two three-project scenarios have identical kit
prompts/rules; their separate kit totals reflect trial variability.

| Scenario | Client | Direct | Improved | Total change | Paired reduction range† |
|---|---|---:|---:|---:|---:|
| 1 project / full baseline | Codex | 445,649 | 356,625 | **20.0% less** | +9.4% … +29.3% |
| 1 project / full baseline | Claude Code | 308,372 | 160,313 | **48.0% less** | +48.0% … +48.1% |
| 1 project / full baseline | Cursor | 323,855 | 332,870 | **2.8% more** | -9.1% … +3.5% |
| 3 projects / full-read instruction* | Codex | 703,457 | 329,232 | **53.2% less** | +51.9% … +54.5% |
| 3 projects / full-read instruction* | Claude Code | 285,717 | 176,804 | **38.1% less** | +33.1% … +42.5% |
| 3 projects / full-read instruction* | Cursor | 508,440 | 301,261 | **40.7% less** | +38.6% … +42.5% |
| 3 projects / focused baseline | Codex | 341,713 | 355,063 | **3.9% more** | -13.6% … +5.8% |
| 3 projects / focused baseline | Claude Code | 257,469 | 177,192 | **31.2% less** | +31.0% … +31.3% |
| 3 projects / focused baseline | Cursor | 271,605 | 277,494 | **2.2% more** | -2.2% … -2.1% |

*Full-read instructions did not produce a perfectly controlled full-read workflow. Codex recovered truncated output with section reads; Claude switched to focused reads on resumptions in one repetition, while retaining full-read attempts in the other. Cursor used full-output recovery in one repetition and switched to section/partial reads in the other. Cursor also searched headings across all 12 project files once, including nine irrelevant notes. Those extra reads and two recovered Claude permission denials are included. Treat these as observed agent workflows, not a clean estimate of full-text ingestion cost. The focused baseline is the stronger alternative for an efficient user.

## Retrieval behavior and correctness

- Current kit: **72/72 exact answer objects**, **63/72 strict JSON-only** replies.
  Cursor sometimes included commentary; those format failures remain.
- Both published methods: **144/144 exact objects**, **129/144 strict JSON-only**.
- All 36 sessions used zero tools on the immediate follow-up and returned the
  updated channel after the controlled blue → teal change. Direct reading also
  detected the update; freshness is not unique to the kit.
- All 18 kit sessions had the required initial hashes, unchanged status/hash
  evidence on turn 3, and only the changed note's CONTENT/new hash on turn 4.
- The edit preserved byte size and nanosecond mtime. Separate regression tests
  also change an omitted section with the same metadata and verify detection.
  Compact project-section filters do not drop the policy.

Across six kit sessions / 24 turns per client, Codex and Claude each made 18
helper calls: **1 / 0 / 1 / 1** for initial / immediate / unchanged / changed.
Cursor made 22 calls, including separate policy or missing-section reads; it used
`--compact` on 9 of those calls. All extra calls count. Rules guide behavior,
but do not guarantee perfect model adherence. Tool-body bytes exclude wrappers
and are not full model input.

## Interpretation

Read known relevant headings on the first call, batch notes with policy, retain
selection and full hashes, and reuse known facts on immediate follow-ups. Never
skip required unread evidence just to reduce a counter. Already-focused direct
reads remain competitive: Codex used 3.9% more and Cursor 2.2% more in that
condition, while Claude used 31.2% less.

This is known-file extraction from templated fiction, not semantic search,
real-business accuracy or whole-note summarization. Models were GPT-6.1-sol and
Claude Opus 5 at medium effort, and Composer 2.5 at default effort, on macOS CLIs.
Caches were not flushed; startup context was not fully isolated. Two repetitions
cannot establish universal rates, a note-length threshold, Windows savings or
short-note v0.1.2 savings. [Full conditions and source hashes](PROTOCOL.md).

## Data and reproduction

- [One-project results](single-full/results.json) · [CSV](single-full/per-turn.csv)
- [Three-project full-instruction results](multi-full/results.json) · [CSV](multi-full/per-turn.csv)
- [Three-project focused results](multi-focused/results.json) · [CSV](multi-focused/per-turn.csv)
- [Current two-method runner](../revision_tokens.py) · [Exporter and evidence checks](../aggregate_revision.py)

Public data contains counters, fictional answers, sanitized tool actions, source
hashes, prompts and update proofs. Raw logs, machine paths, account/session IDs,
real work notes, publication drafts and earlier-version results are excluded.
Source file hashes identify the measured runtime independently of Git history.
