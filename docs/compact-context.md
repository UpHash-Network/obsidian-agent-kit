# Compact context reads (v0.1.2)

The shared rule now prints the installed command once. Supply the selected scope
and batch the relevant files with their policy. When the needed headings are
known, select them on the first read rather than fetching a default excerpt and
then discovering that a required section was omitted.

```sh
obsidian-context demo --compact \
  --file 'Policies/Knowledge policy.md' --file 'Projects/Lighthouse.md' \
  --section 'Current decisions|Release gates'
```

Use the actual command emitted by setup or demo initialization on your PC. Scope,
paths and headings above are examples; the default public sample has different
headings from the long-note benchmark. Select the headings your task needs.

`--compact` removes mtime and byte size from JSON output. It still opens and
hashes the **entire file** with SHA-256 and uses the same stable-read checks.
It does not use timestamps as a shortcut, create a cache or contact a server.
Existing calls without this flag retain the metadata fields.

In a compact batch containing a policy plus other notes, project `--section`
patterns do not filter the policy. Its normal full/partial excerpt and the
combined character budget still apply. A policy-only request can select a section.

Selected headings include their nested subsections. Markdown fenced code blocks
do not create structural headings. An explicit, fully returned selection ends
with `selected sections complete; other sections omitted` instead of repeating a
large outline. This does **not** mean that the whole note was read. Missing matches
and truncated selections are labeled separately; fetch needed missing material.

Retain the full hash and the section selection in the conversation. On substantive
resumption, check the required notes and policy together, using the same selection:

```sh
obsidian-context demo --compact \
  --check 'Policies/Knowledge policy.md=FULL_POLICY_SHA256' \
  --check 'Projects/Lighthouse.md=FULL_NOTE_SHA256' \
  --section 'Current decisions|Release gates'
```

Replace both hash placeholders with the real 64-character values. `UNCHANGED`
permits reuse of already-read facts; `CONTENT` supplies fresh text and a new hash.
Changing an omitted section still changes the hash. If you need a previously
unread section, use `--force` for that file even if its hash is unchanged. A changed
file never makes unread sections known. Check for missing/truncated evidence,
and honor edit tools' read requirements before writing.

The existing install/doctor workflow updates the helper and three managed rule
blocks, preserving surrounding user content. Global installs are explicit; the
benchmark and demo do not update your real work vaults or global AI settings.
Local hash checks do not establish remote Git freshness; keep the team's sync
procedure. Token benefits must be measured separately from these behavior checks.

## 日本語

v0.1.2では共通ルール内のコマンドを1回だけ記載し、必要な章が既知なら初回から
`--section`でまとめて取得します。`--compact`は出力する更新時刻・サイズを省きますが、
**ファイル全体のSHA-256と読込中の変更確認は維持**します。

指定した章には下位の節も含みます。指定範囲をすべて返せた場合は大きな目次を繰り返さず、
「指定章は取得済み、その他は未読」と表示します。一致なし・途中省略を取得済みとして扱いません。
方針と案件を一緒に読むcompactモードでは、案件用の章指定で方針を除外しません。

再開時も同じ章指定で、保持した完全なハッシュをまとめて確認します。未読部分だけの変更も検出します。
未読の章が必要になった場合は、そのファイルだけ`--force`で取得してください。
本文の省略率と総トークンの削減率は異なるため、実モデルでの測定結果も確認してください。
