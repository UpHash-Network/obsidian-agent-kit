# v0.1.2の検証 — Mac・Windows

[English](verification.md) · [導入ガイド](setup.ja.md)

検証には架空ノートを使います。実行ログ、設定、アカウント情報、PC固有のパスはローカルに
置きます。`doctor` の成功に加えて、普段のAIセッションでの動作を確認してください。
補助コマンドは読み取り専用です。保存にはAIツールの通常の編集機能を使います。

## 自動テスト

v0.1.2のキットのフォルダで実行します。

Mac:

```sh
python3 -m unittest discover -s tests -v
```

Windows PowerShell:

```powershell
py -3 -m unittest discover -s tests -v
```

テストは架空データ・一時フォルダ・隔離ホームを使い、AIのAPI、業務Vault、グローバル設定の
編集は行いません。同サイズ・同mtimeの更新検知、未変更本文の省略、読込中の変更、欠落、
取得範囲、パス逸脱・重複scopeの拒否、既存ルールの保持、再install、空白・日本語パス、
起動コマンド、doctor、デモを確認します。v0.1.2ではcompact、未表示章だけの変更、
子見出し・コード内見出し、切り詰め・見出し不一致、章指定時の方針全文保持も確認します。
Windowsのシンボリックリンク作成権限がない場合、その項目はskipになることがあります。

## 隔離デモの確認

[READMEのデモ](../README.ja.md#架空のデモを試す)を使い、各ツールに新しいデモ保存先と会話を
用意します。対応するcodex／claude／cursorフォルダを開き、通常のログイン・信頼確認・
対象を絞った権限確認を済ませます。実Vaultには触れず、権限を回避するフラグは使いません。
実モデルを呼ぶ検証には、各ツールのアカウントとトークンを使います。

| 順番 | 依頼・操作 | 確認すること |
|---|---|---|
| 初回 | Lighthouseのchannel、reviewer、release条件を確認 | helper 1回で方針と案件を取得。blue／Mira／承認が必要／日付未定 |
| 直後 | 会話内の事実だけを言い換える | ツール0回 |
| 未変更の再開 | ローカルの最新の決定と方針を確認 | 両ハッシュを1回で照合、両方UNCHANGED |
| 外部更新 | Macは `python3 demo.py change --dest ../oak-demo`、Windowsは `py -3 demo.py change --dest ../oak-demo` | 実際のデモ保存先に置換。blue→teal、サイズ・mtime保持 |
| 更新後の再開 | 再び最新の決定と方針を確認 | ハッシュ確認1回でtealを取得 |
| 保存 | 「架空のrelease checklistにrollback testを含めることを承認します。既存ノートへ保存し、注記を保持して確認してください」 | 編集前確認、限定的な編集、保存後確認。出典にこの架空検証の承認を記録 |
| 別ツール | 同じデモの別ツール用フォルダで新しい会話を開始 | 保存したrollback testを新たに読み取る。未承認の案は決定にしない |

`../oak-demo` は作成時の保存先に置き換えます。headless／print実行では通常の承認確認が
できない場合があります。まず対話モードで、固定helperコマンドと対象の架空ノートの編集だけを
許可します。helperが拒否されて通常Readで正答しても、helper運用の検証としては不合格です。
Python全体を許可せず、helper・configまで固定します。Claudeの絶対パス指定は
`Edit(//absolute/path)` の形式で、WindowsのドライブはPOSIX形式へ正規化されます。
Codexの保存先は許可された書込範囲に含めます。再開時も許可を確認してください。
[Cursor公式資料](https://cursor.com/docs/cli/reference/permissions)・
[Claude公式資料](https://code.claude.com/docs/en/permissions)を参照できます。

## 日常環境の動作確認

隔離デモのプロジェクトルールだけでなく、インストール済みのグローバルルールと
[短い呼出し補足](setup.ja.md#日常の呼出し例を更新後も保持する)を確認する手順です。
各PCの各ツールで実施します。**普段のホーム・ログイン・インストール済みhelper**を使い、
検証専用のHOME、CODEX_HOME、CLAUDE_CONFIG_DIRへ切り替えません。普段から独自ホームを
使う場合はinstallerの指定と一致させます。検証プロンプトにルール全文を貼り付けたり、
デモのプロジェクトルールを持ち込んだりして成功扱いにしません。

### 架空ノートを1件準備する

1. v0.1.2のcheckoutで `setup.py doctor` を実行し、`PASS local checks` を確認します。
2. 設定済みのチームVaultに、未使用のローカル検証フォルダ `Local checks` を選びます。
   作成前に、Vaultで `git rev-parse --git-path info/exclude` を実行して表示される
   **そのrepoのローカル除外ファイル**へ `/Local checks/` を追加します。一時検証のために
   チーム共有のignore方針は変更しません。Gitなしのローカル専用Vaultならこの操作は不要です。
3. そのVaultで `git check-ignore -- 'Local checks/Agent Kit check.md'` がパスを表示し、
   `git ls-files -- 'Local checks/'` が空であることを確認します。ignoreは追跡済みファイルを
   除外しません。条件を満たさなければ、未使用で除外済みのフォルダを選び直します。
4. `Local checks/Agent Kit check.md` を次の内容で新規作成します。scope名が異なる場合だけ
   `scope: team` を置換します。既存ノートは上書きせず、比較用のコピーをローカルに保持します。

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

設定済みVaultをAIの作業フォルダとして開き、編集できる通常の**Agent**で新しい会話を
開始します。ログイン・信頼確認・限定的な権限確認を済ませます。CursorはUser Ruleを
保存後に再度開き、意図した全文と一致することを確認してください。Askの会話が再開後も
編集を拒否する場合は、新しいAgent会話で最初から検証し、別試行の結果を混ぜません。

### 依頼文と合格条件

`team` と `Policies/Knowledge policy.md` は設定したscope／方針に置き換えます。
1ツールの全段階を**同じ会話**で実施し、4と5の間だけ外部から編集します。
helper 1呼出しとモデル1ターンは別です。余分な探索や失敗呼出しも隠さず記録します。

| 段階 | 依頼・操作 | 必要な証拠 |
|---|---|---|
| 1. ルール認識 | 「ツールを呼ばず、現在適用されているObsidianのscope、helper、compact、更新確認のルールを要約してください。不明なら不明と答えてください」 | ツール0回、推測でなく適用済みルールと一致。これだけで合格にはしない |
| 2. 初回 | 「teamの Local checks/Agent Kit check.md のCurrent decisionsとConstraintsだけを、設定済み方針と一緒に読み、channel・reviewer・release条件を答えてください。編集は不要です」 | helper 1回、compact、ノート＋方針のfile指定、同じ章指定、両ファイルの完全SHA-256。blue／Mira／承認が必要／日付未定 |
| 3. 直後 | 「この会話で確認済みの事実だけを1文に言い換えてください。追加確認は不要です」 | ツール0回。Read・検索・stat・helperを呼ばない |
| 4. 未変更の再開 | 「作業を再開します。同じノートと方針の更新を確認してください。章指定は保持してください」 | 両方の実際の完全ハッシュを1回のcompact checkで照合。同じ章指定、両方UNCHANGED、本文の再出力なし |
| 外部更新 | 下のOS別コマンドを**会話の外で**実行 | blue→teal、ハッシュのみ変更、サイズ・mtimeは同じ。AIには変更後の値を教えない |
| 5. 更新後の再開 | 「作業を再開します。同じノートと方針の更新を確認し、現在のchannelを答えてください。章指定は保持してください」 | compact check 1回、ノートCONTENTでteal、方針UNCHANGED。新しいハッシュを使用 |
| 6. 承認した保存 | 「この架空検証だけ、Validationの Pending. を Confirmed demo decision: add a rollback test. に1回だけ置換して保存することを承認します。他の本文と注記は保持し、編集前の更新確認と保存後の検証をしてください」 | 編集前確認、許可された限定編集、保存後の内容・ハッシュ確認1回。指定文が1回だけあり、他の全バイトが保存前コピーと一致。編集ツールの要件や未読章の取得はこの段階では可 |
| 7. 新しい会話 | 新規会話で現在のchannelと保存したValidationを質問 | tealと保存文を新たに読み取る。以前の会話・別AIのハッシュや知識を持つと仮定しない |

初回・再開時の章指定は `--section 'Current decisions|Constraints'` です。
方針には案件の章フィルターが掛からないことを確認します。`partial` を全文取得とみなさず、
必要な未読章は追加取得します。エラーを `UNCHANGED` と扱いません。

### サイズ・mtimeを保った変更

以下は導入ガイドのTeam Vault配置を使います。別の場所なら `note = ...` だけを
**架空の検証ノート**のパスに変えてください。業務ノートへ実行しません。
同時保存を防ぐため、この操作中はノートの編集画面を閉じます。変更済みの検証ノートは拒否します。

Mac:

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

保存段階の前に、変更後の架空ファイルをVault外にコピーし、全バイト比較に使います。
各ツールの検証後は結果をVault外へ保管し、次のツールでは元の架空ノートと新規会話を使います。
全ツールの完了後は、一時ファイル・自分で追加したignore行・試験用の書込許可だけを撤去します。
固定helperの読取実行許可や他の設定は保持し、架空ファイルやログがstageされていないことを確認します。

### 失敗時の確認と完了記録

| 症状 | 対応 |
|---|---|
| doctor成功でもAIがルールを知らない | 実際のホームと指示ファイル読込先を確認。Cursor User Rulesを再度開き、新しい会話で確認 |
| helper拒否後にReadへ切り替わる | その試行は不合格。対話モードで固定helperを許可して、新規会話でやり直す |
| Windows ClaudeでPowerShell実行が拒否される | Bash／PowerShellの実ツールと許可を照合し、必要なら[Claudeだけのコマンド調整](setup.ja.md#信頼確認と補助コマンドの実行許可)を行う |
| Cursorで読めるが保存できない | Askの再開ではなく新規Agent会話で、対象の編集だけを許可 |
| 方針やcompactが抜ける | 呼出し補足と、重複・矛盾するルールを確認して再検証 |
| 章が切り詰め・不一致になる | 章指定を直すかcharsを増やし、必要な事実を省略しない |
| 別メンバーの変更が見えない | 対応する非公開Vaultをpullしてから確認。helperはGitHubではなくローカルのバイトを照合 |

2026-10-22のメンテナー検証では、Mac・Windowsネイティブの3ツールすべてで、通常ホーム・
短い呼出し補足・固定helper権限を使い、初回1／即時再利用0／未変更1／更新検知1と、
承認文の1回保存・他部分の全バイト保持に成功しました。これは動作確認であり、新たな
トークン計測や全バージョンでの動作保証ではありません。PC設定・実行ログは公開しません。

メンバーごとにOS／Python／kit／client／modelのバージョン、各段階の合否と呼出し数、日付を
記録します。ローカル詳細は非公開記録に置きます。下表を埋め、メンテナーの成功を理由に
別メンバーのPCを確認済み扱いにしないでください。

| 環境 | Codex | Claude Code | Cursor |
|---|---|---|---|
| Mac | 未確認 | 未確認 | 未確認 |
| Windows | 未確認 | 未確認 | 未確認 |

## トークン数の比較

固定の削減率は保証しません。[v0.1.2の長文比較](../benchmarks/v0.1.2/README.ja.md)には
直接読込と現行キットの36セッション・144ターンを掲載しています。既存の測定バッチから
この2方式を取り出したもので、再測定ではありません。除外した方式の実行位置や
キャッシュの限界は測定条件に記載し、採用した2方式の全試行を残しています。
減った条件と増えた条件、status・hash、正答確認、ばらつきも確認してください。

自分の比較では同じ質問・ノート・モデル・出力条件・開始状態をそろえ、順番を入れ替えて複数回
測定します。正答・更新検知とともに、入力全体、キャッシュ入力、出力、確認できる請求量を
区別します。ツールごとの集計は異なり、トークン数・料金・アカウント使用率は同じではありません。
再読込0回もトークン0の意味ではありません。

架空デモは動作確認用です。トークン比較は長い架空の英語ノートから既知の情報を取得する
課題で、実業務の正確さや意味検索の測定ではありません。短いルールや少ない呼出しだけで
総トークンの削減を断定しないでください。非公開の業務データの測定は含めていません。
