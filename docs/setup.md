# v0.1.2 setup and operations — Mac and Windows

[<img src="../examples/demo-vault/Assets/UPHASH/logo.png" alt="UPHASH" width="128">](https://uphash.net/)

**Obsidian Agent Kit — by [UPHASH](https://uphash.net/)**

[日本語](setup.ja.md) · [MIT License](../LICENSE) · [Sharing and branding](branding.md)

The code, shared rules, this guide and fictional examples are MIT licensed.
Keep the copyright and license notices when copying or redistributing them.
Your own knowledge vault may remain private; no UPHASH account or subscription is
needed. The included logo has separate attribution terms in the branding guide.

For each member: get v0.1.2 → open the team's private vault → configure this PC →
activate all three clients → run the [installed-environment check](verification.md#installed-environment-check).
Each person uses their own GitHub access and AI accounts. Installing Obsidian alone
does not install the helper, share a vault, or enable AI rules.

## 0. Requirements and the pinned release

Install Git, Python **3.10 or newer**, Obsidian, and the AI clients you use.
Complete each client's normal login; a desktop login does not necessarily sign
in its CLI. Native Windows PowerShell and macOS Terminal are covered below.
WSL has a separate home and Python environment: install/configure inside WSL if
that is where the AI runs; do not mix its paths with a native Windows install.
No GPU, model download, MCP server or extra Python package is required by the kit.
Transcription and meeting-approval extensions are not included in v0.1.2.

From a parent directory you choose, run these commands in either terminal:

```sh
git --version
git clone --branch v0.1.2 --depth 1 https://github.com/UpHash-Network/obsidian-agent-kit.git
cd obsidian-agent-kit
git describe --tags --exact-match
```

The last line must be `v0.1.2`; a detached checkout at a release tag is expected.
Check Python with `python3 --version` on Mac or `py -3 --version` in PowerShell.
If `py` is unavailable, use the verified Python 3.10+ executable consistently.
For an existing checkout use [Update or remove](#6-update-or-remove).
Use the tagged code and the current guide for a consistent installation.
Keep using the [latest guide](https://github.com/UpHash-Network/obsidian-agent-kit/blob/main/docs/setup.md)
while installing the pinned v0.1.2 code.

## Use knowledge with less repeated context

The kit is designed to reduce unnecessary input tokens by retrieving relevant
notes, reusing facts already in the conversation, and returning compact change
checks instead of duplicate note bodies. A changed note returns its current
excerpt so savings do not depend on deliberately ignoring updates.

To get the benefit, keep project decisions concise, install the shared rule only
once per workspace, and ask for the specific project or topic. Use no new note
call for an immediate follow-up using known facts; verify freshness on substantive
resumption or before edits. Read necessary omitted sections even when they exceed
the default excerpt budget. Start fresh after lost context rather than assuming
another AI shares the old conversation's hashes or knowledge.

Rules and checks also cost tokens, and existing conversation history may be
charged again. Tiny tasks may not save tokens. See [how savings work](../README.md#how-this-can-save-tokens)
and [how to compare usage](verification.md#token-measurement). Measure totals with
the same task/model and check correctness; zero new note calls does not mean a
zero-token model response or a guaranteed billing reduction.

In v0.1.2, use the generated `--compact` rule and select known headings on the
first call. Keep that selection on resumed hash checks; fetch relevant unread
sections when needed. [Compact reads](compact-context.md) explains coverage,
policy handling and the unchanged whole-file hash check. The
[v0.1.2 long-note comparison](../benchmarks/v0.1.2/README.md) includes every
current-kit versus direct-read trial, both savings and increases, with conditions.

## 1. Try the isolated demo

Follow the [README](../README.md). It needs Python 3.10+ and creates only a new
directory. Each client gets one copy of the same rule, avoiding duplicated rules
inside a single demo workspace. Open the matching client directory, finish normal
authentication/trust, and begin a new conversation. Start with `Welcome.md` in
the generated vault for links and the exercise. Obsidian can remain closed
when using the helper. A new demo is enough to reset the exercise.

## 2. Prepare your own vaults

Create separate, non-overlapping vault directories for each team/company and a
separate local personal vault. Use Obsidian's normal vault creation/open workflow.
Create `Policies/Knowledge policy.md` in each vault using the sample's structure,
but replace the fictional/demo policy with your actual approved scope, retention
and sync policy. Add YAML scope, asset_type, status, project and date to notes.

Record decisions, rationale, constraints and references. Keep code in its own
repository. Do not copy the demo's fictional decisions into production projects.
The helper does not create your policies or infer who owns a project.

For shared knowledge, create a **separate private Git repository** for each team.
Invite only that team's members, review staged files, then commit/push. Other PCs
clone that private repository and open its directory in Obsidian. Configure their
own local paths below; do not commit machine configurations. Personal scope is
local-only in v0.1. The public toolkit repository must never become your work vault.

The team maintainer chooses the repository, scope name, owner and approved policy.
Members clone that repository into their own vault location; they do not create a
second copy of the team's history. For example, after creating the parent folder:

Mac:

```sh
mkdir -p "$HOME/Documents/Knowledge"
git clone https://github.com/your-github-organization/team-knowledge.git "$HOME/Documents/Knowledge/Team"
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE/Documents/Knowledge" | Out-Null
git clone https://github.com/your-github-organization/team-knowledge.git "$env:USERPROFILE/Documents/Knowledge/Team"
```

The repository and owner above are placeholders. Open the resulting Team directory
as an existing vault in Obsidian. Its approved policy must exist before `doctor`.
An optional Personal vault also needs its own policy before configuring it.

The sample vault includes baseline ignore patterns. Review them for your data;
ignore rules do not remove already-tracked files. Use your team's existing Git
sync method, or `git pull --ff-only` at work start and a reviewed commit/push at
work end. If local changes or remote divergence prevent pulling, resolve them
before continuing. No force-push or automatic conflict resolution is provided.

## 3. Configure each PC

Run from the toolkit checkout. These commands write configuration under your
home directory; they do not modify vault contents. Replace sample paths and
`your-github-organization` with your values. An owner is the GitHub organization
or user from a credential-redacted project remote. Explicit ownership exceptions
in your rules take priority; a folder's parent name does not determine ownership.

macOS / Linux:

```sh
python3 setup.py configure --scope team --vault "$HOME/Documents/Knowledge/Team" --owner your-github-organization
python3 setup.py install
python3 setup.py doctor
```

Windows PowerShell:

```powershell
py -3 setup.py configure --scope team --vault "$env:USERPROFILE/Documents/Knowledge/Team" --owner your-github-organization
py -3 setup.py install
py -3 setup.py doctor
```

Default policy: `Policies/Knowledge policy.md`. Use `--policy 'relative/path.md'`
if needed. Repeat configure with a distinct scope/root for each team. Omit personal
if you do not need it; unknown/mixed work must then ask for a destination, not fall
back to a company. Use `--local-only` for a local-only team scope.
To add personal notes, configure `--scope personal --vault <personal-vault>` after
creating its policy, then rerun install/doctor. Replace `<personal-vault>` with a
quoted path; `personal` is always local-only. `PASS local checks` is the expected
doctor result. Do not continue past a missing-policy or helper-mismatch error.

Defaults and overrides:

| Item | Default / option |
|---|---|
| Configuration | `~/.config/obsidian-context/config.json`; `--config` or `OBSIDIAN_CONTEXT_CONFIG` |
| Installed helper and backups | `~/.local/share/obsidian-context/` |
| Installed MIT notice | `~/.local/share/obsidian-context/LICENSE` |
| Launcher | `~/.local/bin/obsidian-context` (`.cmd` on Windows) |
| Codex rules | `~/.codex/AGENTS.md`; `--codex-home` or existing `CODEX_HOME` |
| Claude rules | `~/.claude/CLAUDE.md`; `--claude-home` or existing `CLAUDE_CONFIG_DIR` |
| Cursor rule text | `~/.local/share/obsidian-context/cursor-user-rule.txt` |

`--home` is available for isolated installer tests. Installation updates only the
marked Obsidian block in existing instruction files; other rules are preserved.
Changed files get byte-for-byte backups. Malformed markers cause an error. A known
unmarked legacy section requires manual review before `--migrate-legacy`.

## 4. Activate client rules

- **Codex:** restart/start a new session after installation; inspect `AGENTS.md`
  loading in your client and run the acceptance check.
- **Claude Code:** start a new session so the updated `CLAUDE.md` takes effect.
- **Cursor:** open Settings → Rules/User Rules (location varies by version), paste
  the generated `cursor-user-rule.txt`, and replace any older Obsidian rule.
  A file in `~/.cursor/rules` is only a compatibility reference and does **not**
  automatically enable a global rule. The demo's `.cursor/rules/*.mdc` is a real
  project rule; avoid adding the same full rule twice to one workspace.

For Cursor, open the generated text with `open -e "$HOME/.local/share/obsidian-context/cursor-user-rule.txt"`
on Mac, or `notepad "$env:USERPROFILE/.local/share/obsidian-context/cursor-user-rule.txt"`
in PowerShell. Save the UI rule, reopen it, and compare the full text. Preserve
unrelated language/style rules. Use a fresh **Agent** conversation for read-and-save
verification; an Ask/Plan conversation can remain read-only when resumed.

### Keep the daily-call clarification across upgrades

The v0.1.2 installer supplies the short core rule. For the same explicit call
pattern used in the installed-environment checks, add this small local supplement
once to Codex's `AGENTS.md`, Claude's `CLAUDE.md`, and the Cursor User Rule:

```markdown
<!-- obsidian-local-calls:begin -->
### Daily helper calls
Use the installed command and configured scope/policy paths.
Every normal read/check includes --compact.
Known-file first read: SCOPE --compact --file 'note.md' --file 'POLICY.md' --section 'needed headings'.
Resume: SCOPE --compact --check 'note.md=FULL_NOTE_SHA256' --check 'POLICY.md=FULL_POLICY_SHA256' --section 'needed headings'.
Replace POLICY.md with this scope's configured policy. A bare --file does not add it.
Keep full hashes in the conversation; immediate follow-ups make zero calls.
If permission is denied, report it and resolve the exact helper permission; do not silently switch to repeated raw reads.
<!-- obsidian-local-calls:end -->
```

Place it **outside** the installer's `obsidian-context:begin/end` block so reinstall
preserves it. Keep existing ownership exceptions, meeting workflows and annotations
outside that block too. The installer does not add this supplement or copy custom
workflow extensions. After an upgrade, update the core Cursor UI rule from generated
text while retaining the supplement once; keep a local copy of the full UI text.
Only use a section filter when the needed headings are known; otherwise omit it
on the first read and choose the relevant sections from the result.

### Trust and the helper's execution permission

Open only the intended workspace, inspect it, and complete its normal trust prompt.
Approve the installed helper command with its fixed executable/script/config;
note writes need separate permission. Keep existing deny rules. A correct answer
obtained by falling back to raw reads after a denied helper is not a passing check.
Headless/print mode may wait for approval it cannot display: finish setup in an
interactive session first. Do not disable approval checks to make it pass.

The installed command uses the Python interpreter that ran setup. On Windows the
generated AI rule uses PowerShell quoting. If Python is moved/removed, rerun
installation with the new interpreter. Complete normal workspace-trust and
permission prompts. Do not disable client security checks to make a test pass.

**Windows Claude Code:** inspect which tool actually executes the command.
A PowerShell permission does not authorize a Bash call. If the client uses Bash,
add a Claude-only local command override (outside the managed block) with the same
installed Python executable, helper and configuration in Bash-compatible quoting:

```text
"<python-executable>" "<installed-helper>" --config "<config-file>" team --compact ...
```

Replace all placeholders locally with the paths printed by install; use forward
slashes where needed and omit PowerShell's leading `&`. Approve only that fixed
command, then verify its actual invocation in a new session. Do not add blanket
Python, Bash or PowerShell permissions. Keep the generated PowerShell command for
clients that use PowerShell. The core helper remains the same v0.1.2 file.
See [Claude permissions](https://code.claude.com/docs/en/permissions) and
[Cursor CLI permissions](https://cursor.com/docs/cli/reference/permissions) for
the installed client's matching syntax; UI and CLI permissions can differ.

`doctor` checks local files and helper behavior. It cannot certify Cursor's UI
setting, model obedience, provider login, or remote Git freshness. Follow
[verification](verification.md) in each client after setup or a major upgrade.
Run the installed-environment check with your **normal home and login**, no pasted
rule text in the test prompt, and only a fictional note. A successful isolated demo
does not prove the global rules are active.

## 5. Everyday commands

The generated rule contains the exact command for that PC. You can also use the
source helper (Windows: replace `python3` with `py -3`):

```sh
python3 obsidian_context.py team --compact --query 'Exact note title'
python3 obsidian_context.py team --compact --file 'Policies/Knowledge policy.md' --file 'Projects/Example.md'
python3 obsidian_context.py team --compact --check 'Policies/Knowledge policy.md=FULL_POLICY_SHA256' --check 'Projects/Example.md=FULL_NOTE_SHA256'
```

Replace each hash placeholder with the **actual 64-character hash** for that file.
Batch policy and known notes in the same call. Query searches filenames, not full
text or embeddings. An exact unique stem loads that note and policy; otherwise
it returns candidate names. Select relevant candidates only. For broader searches,
use a scoped text search yourself; a semantic-search engine is not part of v0.1.

If required headings are known, append the same `--section 'Heading1|Heading2'`
to the first read and resumed checks. [Selection and coverage](compact-context.md)
explains how to handle partial results and newly needed sections.

`UNCHANGED` permits reusing already-read facts. `CONTENT` includes a fresh excerpt.
`coverage: partial` is not a full read: inspect relevant omitted sections with
`--force --section 'Heading pattern'` or a larger `--chars` budget. Lost context
requires a fresh read. `ERROR`, missing files and Git conflicts are not unchanged
facts. The hash represents local bytes, not the latest remote commit.

After confirmed decisions, an authorized editor updates the existing note,
preserving annotations, then checks the changed section once. Rules do not turn
unapproved proposals or meeting transcripts into approved decisions.

## 6. Update or remove

This repository starts with a fresh release history. If an existing checkout
belongs to an earlier repository or Git reports unrelated histories, clone into
a new directory and reinstall from there. Preserve your local configuration and
custom rules; do not merge the earlier repository's history into this one.


Before upgrading, review release notes and back up your rules. In a clean toolkit
checkout, fetch tags and select the intended release (`v0.1.2` for compact reads),
then rerun install and doctor; paste regenerated Cursor User Rules again. Do not
switch Git revisions over uncommitted work. Review release and license notices.
The toolkit does not silently update itself or your teammates' installations.

```sh
git status --short
git fetch origin --tags
git switch --detach v0.1.2
```

Stop before switching if the first command shows changes. Back up custom text
inside the managed block and move it outside before installing. On each PC use
the same configure/install/doctor and client activation steps above. Verify the
helper against that checkout with doctor, then repeat the [acceptance checks](verification.md#installed-environment-check).
Retain old backups until the new setup passes; do not overwrite later manual edits
when restoring a backup. Send teammates guide links, not your config, credentials,
global settings backups or logs.

To remove global integration, delete **only** the region from
`<!-- obsidian-context:begin -->` through `<!-- obsidian-context:end -->` in the
Codex/Claude files and Cursor compatibility file, and remove the corresponding
Cursor User Rule in the UI. Preserve all other instructions. Once unused, remove
the launcher, helper directory and configuration. Backups live inside the helper
directory; preserve needed backups first. Never remove vaults as part of uninstall.
To roll back, use an appropriate backup after checking for subsequent manual edits.

Removing an isolated demo requires only removing that generated directory after
preserving any changes you want. It has no global setup to undo.

## Share what worked

You can link to [Obsidian Agent Kit by UPHASH](https://github.com/UpHash-Network/obsidian-agent-kit)
or use the optional badge from the [branding guide](branding.md) in your own README.
An attribution link helps new users find the original guides and updates.
UI promotion is optional; retain the MIT notices when redistributing covered files.
Use fictional examples for public feedback. [About UPHASH](https://uphash.net/).

Official references: [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md),
[Claude Code memory](https://code.claude.com/docs/en/memory),
[Cursor rules](https://cursor.com/docs/rules).
