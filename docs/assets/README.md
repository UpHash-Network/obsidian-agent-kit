# v0.1.2 sharing graphics / 投稿用画像

Created with built-in image_gen on 2026-10-22. English and Japanese PNGs are
1536×1024. The official UPHASH logo was supplied as a brand reference. Final
figures, labels, conditions and arrow directions were visually reviewed.

## Current files / 今回使う画像

- [English PNG](agent-kit-v0.1.2-en.png)
- [日本語PNG](agent-kit-v0.1.2-ja.png)

Use the matching PNG in the format permitted by the destination.
Keep the baseline, each card's project count and all conditions visible.
These are AI-generated explanatory graphics, not client screenshots or vendor endorsements.

GitHub画面のスクリーンショットではなくPNG本体を使います。比較対象・案件数・測定条件を
切り落とさないでください。AI生成の説明図であり、実アプリ画面や各社の公認図ではありません。

## What the figures mean / 数値の意味

The image shows **each client's best whole-workload reduction vs direct reading
among the three published v0.1.2 workloads**. All three cards share the same
baseline type, but the winning project count differs. Each result sums both
four-turn runs; no best-run or best-turn selection.

| Client | Workload | Direct → v0.1.2 total tokens | Reduction |
|---|---|---:|---:|
| Codex | 3 projects, full-read instruction | 703,457 → 329,232 | 53.2% |
| Claude Code | 1 project, full-read instruction | 308,372 → 160,313 | 48.0% |
| Cursor | 3 projects, full-read instruction | 508,440 → 301,261 | 40.7% |

Source: [public counters](../../benchmarks/v0.1.2/summary.json).
Formula: `100 × (direct − improved) / direct`, one decimal.
Twelve fictional English notes, about 28 KB each, plus a policy; exact relevant
files/headings supplied. Mac CLI, two runs × four turns per client/method.
Models: GPT-6.1-sol, Claude Opus 5, Composer 2.5. Caches were not cleared.
Totals include cached input counted once plus output. Full-read instructions
sometimes produced narrowed reads or recovery calls; those count too.

The headline is a **selected maximum in this experiment**, not typical savings,
cost reduction, account-quota savings, a Windows token measurement or a universal
claim. Against already-focused direct reads Codex used 3.9% more, Claude Code
31.2% fewer, Cursor 2.2% more. Those and all other results remain in the
[English report](../../benchmarks/v0.1.2/README.md) and
[日本語の測定結果](../../benchmarks/v0.1.2/README.ja.md).

「最大」は検証3条件中の各ツールの最大値です。各条件の2回を合算し、直接読込との比較に
統一しています。Codex・Cursorは3案件、Claude Codeは1案件での結果です。
比較対象は全文指示ですが、一部のAIは範囲を絞ったり出力の切れに対応したりしています。
全条件で削減できたという意味でも、料金削減率でもありません。
増加した条件も測定ページで公開しています。

## Alt text / 代替テキスト

English:

> Obsidian Agent Kit v0.1.2 by UPHASH. Codex, Claude Code and Cursor read relevant
> Obsidian Markdown notes and save confirmed decisions. Team members edit notes;
> explicit Git sync shares them through a private repository. Best of three
> tested workloads vs direct reading: Codex −53.2% on three projects, Claude Code
> −48.0% on one, Cursor −40.7% on three. Full-read instructions; agents could narrow
> direct reads. Twelve fictional ~28 KB notes; two runs × four turns per client/method.
> Mac CLI, cached input plus output. Other conditions can increase usage; not cost savings.

日本語：

> UPHASHのObsidian Agent Kit v0.1.2。Codex・Claude Code・Cursorが必要なMarkdownノートを読み、
> 確定した決定を保存。メンバーはObsidianで編集し、Gitの同期操作で非公開リポジトリから共有。
> 検証3条件中の直接読込比の最大削減率はCodex 53.2%（3案件）、Claude Code 48.0%（1案件）、
> Cursor 40.7%（3案件）。比較対象は全文指示ですが一部AIは範囲を限定。
> 約28KBの架空ノート12件、各ツール・各方法2回×4ターン、Mac CLI、キャッシュ入力・出力込み。
> 条件により増加し、料金削減率ではありません。

## Attribution / 素材の扱い

Original explanatory text and layout use this repository's MIT license.
UPHASH marks retain the [separate branding terms](../branding.md);
the official logo's [source and notice](../../examples/demo-vault/Assets/UPHASH/README.md)
remain unchanged. Tool names describe compatibility, not endorsement.
No sponsorship or donation links are included.
