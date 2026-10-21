# v0.1.2 verification — Mac and Windows

[日本語](verification.ja.md) · [Setup](setup.md)

Use fictional notes for these checks. Keep raw tool traces, settings, account
details and machine paths local. A successful `doctor` is only the first layer:
check the normal AI sessions as well. The helper is read-only; the client's editor
performs an authorized save.

## Deterministic tests

```sh
python3 -m unittest discover -s tests -v
```

Windows: `py -3 -m unittest discover -s tests -v`.
Tests use temporary fictional files and isolated installation homes. No provider
account, API call, production vault or global rule edit is needed.

Coverage includes full SHA-256 changes despite identical mtime/size, unchanged
body suppression, changes during a read, missing files, partial coverage, scoped
path/symlink rejection, scope overlap rejection, managed-rule preservation,
idempotent installation, non-ASCII/spaced paths, launcher/doctor, and the demo CLI.
v0.1.2 also tests compact output, same-metadata edits confined to omitted sections,
nested/fenced Markdown headings, explicit no-match/truncation markers, and policy
preservation when project sections are selected in a batch.
Symlink tests may skip when Windows does not grant symlink creation permission.

## Isolated demo check

Use a new demo directory for each client and a new conversation. Open the matching
client directory. Finish normal login, workspace trust and scoped tool permission
prompts. Keep the other clients and real vaults out of the exercise. Do not use
permission-bypass flags. Model calls use the client's account and may cost tokens.

Headless/print mode cannot answer ordinary approval prompts for you. A denied
helper call followed by direct file reads is a **failed helper-workflow check**,
even if the answer is correct. Use an interactive session to approve the exact
helper command and intended note edit, or configure narrow local permissions.
In Cursor CLI, `Shell(command:args)` can restrict the Python command to this
helper/config/scope; do not allow all Python commands just for this demo.
Claude Code uses `Edit(//absolute/path/**)` for absolute allow paths, and Codex
needs the demo vault among its writable roots for the save stage. Check permissions
again when resuming a CLI session. The demo generator does not grant permissions.
References: [Cursor CLI permissions](https://cursor.com/docs/cli/reference/permissions),
[Claude Code permissions](https://code.claude.com/docs/en/permissions).

| Stage | Prompt/action | Evidence to inspect |
|---|---|---|
| Initial | Ask Lighthouse channel, reviewer and release conditions | One helper call; policy + Lighthouse; blue/Mira/approval required/date undecided |
| Immediate follow-up | Rephrase using facts already in this chat | Zero tools; no read/search/stat |
| Unchanged substantive resume | Ask to verify current local decisions and policy | One call with both actual hashes; UNCHANGED headers without bodies |
| Changed substantive resume | Run `demo.py change`, then ask again to verify current local decisions and policy | One hash-check call; teal included despite identical mtime/size |
| Save a decision | “I confirm the fictional release checklist must include a rollback test. Save this confirmed decision to the existing Lighthouse note, preserve annotations, and verify it.” | Freshness check before edit; focused edit; one verification; valid YAML and source explaining this explicit demo instruction |
| Cross-client handoff | Open another client's workspace for the same demo, start a new chat, ask for current Lighthouse decisions | The saved rollback-test decision is found; proposals are not promoted |

Record versions, models, stages, relevant tool counts and pass/fail. Review tool
calls as well as final answers. A correct answer alone does not prove note access
or freshness. Additional client startup discovery may occur; report it separately.
If a client ignores rules, report that result and its actual tool trace; do not
claim automatic adherence. Keep raw client logs local and sanitize shared reports.

## Installed-environment check

This verifies the global installation and the short [daily-call supplement](setup.md#keep-the-daily-call-clarification-across-upgrades),
not only a demo workspace's project rule. Repeat for each client on each PC.
Use the **normal home, login and installed helper**, without alternate HOME,
CODEX_HOME or CLAUDE_CONFIG_DIR values created just for the test. Existing intentional
custom homes should match the installer configuration. Do not paste the rule into
the test prompt or load the demo's project rules to make global activation pass.

### Prepare one fictional note

1. Run `setup.py doctor` from the v0.1.2 checkout; expect `PASS local checks`.
2. In the configured team vault, choose an unused local-only folder called
   `Local checks`. Before creating files, add `/Local checks/` to that repository's
   **local Git exclude file**, found by running `git rev-parse --git-path info/exclude`
   from the vault. Do not change a shared ignore policy for this temporary check.
   For a local-only vault without Git, this step is unnecessary.
3. From that Git vault, run `git check-ignore -- 'Local checks/Agent Kit check.md'`;
   it must print the path. Also check that
   `git ls-files -- 'Local checks/'` is empty: ignore does not untrack existing files.
   If either check fails, choose an unused excluded folder before continuing.
4. Create `Local checks/Agent Kit check.md` with the following fictional content.
   Replace `scope: team` if your configured scope has another name. Do not replace
   an existing note. Keep a local copy for the final comparison.

```markdown
---
scope: team
asset_type: project
status: confirmed
project: agent-kit-check
date: 2026-01-01
---
# Agent Kit check

## Current decisions
Channel: blue
Reviewer: Mira

## Constraints
Reviewer approval is required. No approval is recorded. Release date is undecided.

## Human annotations
Keep this sentence unchanged.

## Validation
Pending.

## Sources
Fictional installation check; no real project or employee data.
```

Open the configured vault as the client's workspace. Start a new normal **Agent**
session capable of editing; complete login, trust and narrowly scoped permissions.
For Cursor, first save/reopen its User Rule and compare it with the intended text.
An Ask-mode conversation can remain read-only on resume; start a fresh Agent
conversation if necessary, and repeat the stages rather than mixing runs.

### Prompts and pass criteria

Replace `team` and `Policies/Knowledge policy.md` with your configured scope and
policy. Run all stages in **one conversation** for a given client, with the external
edit between stages 4 and 5. A shell call means one helper invocation, not a model
turn. Do not hide extra discovery or failed calls when recording results.

| Stage | Prompt or action | Required evidence |
|---|---|---|
| 1. Rule recognition | “Without tools, summarize the Obsidian scope, helper, compact reads and update-check rule currently supplied to you. Say if you do not know.” | No tools. Correct installed rule, not a guessed command. This alone is not a pass. |
| 2. Initial read | “For team scope, read only Current decisions and Constraints in Local checks/Agent Kit check.md together with the configured policy. Give the channel, reviewer and release conditions. Do not edit anything.” | One helper call, `--compact`, both `--file` paths and `--section 'Current decisions\|Constraints'`. Note and policy full SHA-256 retained. Answer: blue, Mira, approval required, date undecided. |
| 3. Immediate reuse | “Restate those confirmed facts in one sentence using only this conversation. No new check is needed.” | Zero tools: no read, search, stat or helper. |
| 4. Unchanged resume | “Resume work. Check the same note and policy for updates, retaining the selected headings.” | One compact call with both actual full `--check` hashes and the same section pattern. Both `UNCHANGED`; no repeated note bodies. |
| External edit | Run the platform command below **outside the AI conversation**. | blue → teal; different hash, same byte count and mtime. Do not tell the AI the new value. |
| 5. Changed resume | “Resume work. Check the same note and policy for updates and report the current channel, retaining the selected headings.” | One compact hash check; note `CONTENT` with teal, policy `UNCHANGED`. The AI uses the new hash. |
| 6. Approved save | “For this fictional check only, I approve replacing Pending. under Validation with Confirmed demo decision: add a rollback test. exactly once. Preserve all other text and annotations. Check freshness before editing and verify the saved result.” | Freshness check, authorized focused edit and one final content/hash verification. The sentence occurs once; all other bytes match your pre-save copy. Extra reads required by the editor or newly needed sections are allowed here. |
| 7. New conversation | Start a fresh conversation and ask for the current fictional note's channel and saved validation decision. | A fresh read discovers teal and the saved sentence. Old hashes/facts are not assumed to carry across conversations or clients. |

The backslash before `|` above only escapes a Markdown table delimiter. The actual
command uses `--section 'Current decisions|Constraints'`. Policy content must stay
unfiltered even when the project headings are selected. Read needed omitted sections
instead of treating `partial` as a complete note. Errors are not `UNCHANGED`.

### Change content while preserving size and mtime

The following example uses the Team vault location from the setup guide. Change
only `note = ...` to your **fictional check note** if you chose another location.
Do not run it on a business note. Close the note's editor during this step so a
concurrent save does not replace the fixture. It refuses an already-changed fixture.

Mac Terminal:

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, os
note = Path.home() / 'Documents/Knowledge/Team/Local checks/Agent Kit check.md'
before = note.read_bytes()
stamp = note.stat()
assert before.count(b'Channel: blue') == 1, 'Use a fresh fictional check note'
after = before.replace(b'Channel: blue', b'Channel: teal', 1)
assert len(before) == len(after)
note.write_bytes(after)
os.utime(note, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
assert note.stat().st_size == stamp.st_size
assert note.stat().st_mtime_ns == stamp.st_mtime_ns
assert hashlib.sha256(before).digest() != hashlib.sha256(note.read_bytes()).digest()
print('PASS: content changed; size and mtime preserved')
PY
```

Windows PowerShell:

```powershell
@'
from pathlib import Path
import hashlib, os
note = Path.home() / 'Documents/Knowledge/Team/Local checks/Agent Kit check.md'
before = note.read_bytes()
stamp = note.stat()
assert before.count(b'Channel: blue') == 1, 'Use a fresh fictional check note'
after = before.replace(b'Channel: blue', b'Channel: teal', 1)
assert len(before) == len(after)
note.write_bytes(after)
os.utime(note, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
assert note.stat().st_size == stamp.st_size
assert note.stat().st_mtime_ns == stamp.st_mtime_ns
assert hashlib.sha256(before).digest() != hashlib.sha256(note.read_bytes()).digest()
print('PASS: content changed; size and mtime preserved')
'@ | py -3 -
```

Before the save stage, keep a copy of this changed fictional file outside the vault
for byte comparison. After each client, archive the fictional result outside the
vault and recreate the original fixture before the next client's new session.
After all clients pass, remove only the temporary files, your added ignore line,
and any test-only write grants. Preserve permissions for the installed read helper
and unrelated settings. Check that no fixture or log is staged for Git.

### Troubleshooting and completion record

| Symptom | Action |
|---|---|
| `doctor` passes but the AI does not know the rule | Check the actual client home and instruction loading; reopen Cursor User Rules; start a new conversation. |
| Helper is denied and the AI uses raw Read instead | Mark this trial failed. In interactive mode approve the fixed helper command; repeat in a new session. |
| Windows Claude rejects a PowerShell command | Check the actual Bash/PowerShell tool and matching permission. Apply the [Claude-only command adjustment](setup.md#trust-and-the-helpers-execution-permission) if needed. |
| Cursor can read but cannot save | Use a new Agent conversation, not a resumed Ask session; grant only the intended edit. |
| Policy or `--compact` is omitted | Check the daily-call supplement and duplicate/conflicting rules, then rerun. |
| A section is truncated or missing | Correct the heading selection or increase `--chars`; do not silently drop needed facts. |
| A colleague's update is not detected | Pull the correct private vault first. The helper checks local bytes, not GitHub. |

On 2026-10-22, maintainer acceptance checks passed on Mac and native Windows for
all three clients, with normal homes, the local call clarification and exact helper
permissions. Each passed initial 1 / immediate reuse 0 / unchanged check 1 /
changed check 1 and a one-time authorized save preserving other bytes. This is a
behavior check, not a new token benchmark or a guarantee for every client version.
Private machine settings and raw traces are intentionally not published.

For each member, record only OS/Python/kit/client/model versions, each stage's
pass/fail and tool counts, and the date. Keep local details in private records.
Use this blank checklist; do not mark another member's environment passed based
on the maintainer result:

| Environment | Codex | Claude Code | Cursor |
|---|---|---|---|
| Mac | Pending | Pending | Pending |
| Windows | Pending | Pending | Pending |

## Token measurement

This release ships no private benchmark corpus and claims no fixed token savings.
The [v0.1.2 long-note comparison](../benchmarks/v0.1.2/README.md) publishes 144 turns
from 36 direct-read/current-kit sessions, with every retained trial, sanitized
counters, status/hash evidence, answer checks and paired variability. It is a
subset of an existing measurement batch, not a new model run. The protocol explains
omitted-arm positions and cache limitations. Results include savings and increases.

For your own comparison, keep the same questions, notes, model, output requirement
and starting conditions; alternate run order and repeat. Measure task correctness
and update detection alongside tokens. Separate total input, cached input, output,
and billed usage where the provider reports them. CLI accounting differs across
clients; totals are not interchangeable with costs or account-limit percentages.

The fictional demo checks behavior. The token benchmark covers known-file
extraction from long fictional English notes, not real-business accuracy or
semantic search. A shorter rule or fewer calls alone does not prove lower total
model usage. No private business-data benchmark is included.

日本語の全文手順は[検証ガイド](verification.ja.md)を参照してください。
