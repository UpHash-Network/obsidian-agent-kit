# v0.1.2の導入と運用 — Mac・Windows

[<img src="../examples/demo-vault/Assets/UPHASH/logo.png" alt="UPHASH" width="128">](https://uphash.net/)

**Obsidian Agent Kit — by [UPHASH](https://uphash.net/)**

[English](setup.md) · [MITライセンス](../LICENSE) · [紹介・ロゴのガイド](branding.md)

コード・共通ルール・このガイド・架空サンプルはMITライセンスです。
コピーや再配布の際は著作権表示と許諾文を保持してください。自分の業務Vaultは
非公開のまま使え、UPHASHのアカウントや契約は不要です。同梱ロゴには別の紹介用途の条件があります。

各メンバーは、v0.1.2取得 → チームの非公開Vaultを開く → PCを設定 → 3ツールで有効化 →
[日常環境の動作確認](verification.ja.md#日常環境の動作確認)の順で進めます。
GitHubの権限とAIのアカウントは各自のものを使います。Obsidianをインストールするだけでは、
補助コマンド・Vaultの共有・AIのルールは設定されません。

## 0. 必要なものとv0.1.2の取得

Git、**Python 3.10以上**、Obsidian、利用するAIツールを用意します。各ツールの通常の
ログインを済ませてください。アプリとCLIの認証は別の場合があります。
以下はMacのターミナルとWindowsネイティブのPowerShell向けです。WSLはホームとPythonが
別なので、AIをWSLで動かす場合はWSL内で導入し、Windows側のパスと混ぜません。
キット自体にGPU、モデルのダウンロード、MCPサーバー、追加Pythonパッケージは不要です。
文字起こしや議事録承認の拡張はv0.1.2に含まれません。

保存先の親フォルダで実行します。以下のGitコマンドは両OSで共通です。

```sh
git --version
git clone --branch v0.1.2 --depth 1 https://github.com/UpHash-Network/obsidian-agent-kit.git
cd obsidian-agent-kit
git describe --tags --exact-match
```

最後の出力が `v0.1.2` であることを確認します。タグ取得後のdetached状態は正常です。
Macは `python3 --version`、PowerShellは `py -3 --version` でPythonを確認します。
`py` がない場合は、確認済みのPython 3.10以上の実行ファイルを一貫して使います。
既存checkoutは[更新・解除](#6-更新解除)へ進みます。
このガイドはmainで更新し、既存のリリースタグは書き換えません。
コードはv0.1.2に固定し、手順は[最新版のガイド](https://github.com/UpHash-Network/obsidian-agent-kit/blob/main/docs/setup.ja.md)を参照してください。

## トークン節約につながる使い方

必要なノートだけを取得し、会話内の既知の事実を再利用し、変更のない本文を短い確認結果に
置き換えることで、余分な入力トークンを減らす設計です。更新があれば新しい抜粋を返します。

案件の決定事項は簡潔に保ち、同じ作業フォルダへ共通ルールを重複登録せず、対象の案件・
話題を指定してください。直後の言い換えは既知の内容を使い、作業再開や編集前には更新を
確認します。必要な未読部分は文字数の目安を超えても読みます。会話が失われた場合や別AIへ
移った場合は、以前の知識やハッシュを把握していると仮定せず、改めて必要なノートを読みます。

ルールや確認処理にもトークンが必要で、既存の会話履歴が再度計上される場合もあります。
短い作業では削減にならないこともあります。[仕組みの説明](../README.ja.md#なぜトークンを節約できるのか)と
[比較手順](verification.ja.md#トークン数の比較)を参考に、同じ課題・モデルで正確さと総量を
確認してください。ノート呼び出し0回は、AIの消費トークンや料金が0になる意味ではありません。

v0.1.2では生成される `--compact` のルールを使い、必要な章が既知なら初回から指定します。
再開時も同じ章指定で更新を確認し、別の未読部分が必要なら追加取得します。
[短い出力の使い方](compact-context.md#日本語)に取得範囲・方針・全体ハッシュの説明、
[直接読込との実測比較](../benchmarks/v0.1.2/README.ja.md)に現行版の全試行を掲載しています。
増えた条件も含めて確認してください。

## 1. まず隔離デモを試す

[README](../README.ja.md)の手順でPython 3.10以上を使います。作成するのは指定した
新しいフォルダだけです。Codex／Claude Code／Cursorそれぞれの作業フォルダに
共通ルールを1つずつ置きます。対象フォルダを開き、通常のログイン・信頼確認を
済ませ、新しい会話を始めます。補助コマンドはObsidianを閉じていても動きます。
Vault内の `Welcome.ja.md` から案内を確認できます。繰り返すときは新しい保存先にデモを作ります。

## 2. 自分のVaultを準備する

会社・チームごとに別々の、入れ子にならないVaultを用意します。個人用も別の
ローカルVaultにします。Obsidianで開き、各Vaultに `Policies/Knowledge policy.md`
を作成します。サンプルの構造を参考に、架空デモの文言を実際に承認された保存方針・
所属・同期方法へ置き換えてください。ノートのYAMLにはscope、asset_type、status、
project、dateを記録します。

保存対象は決定・理由・制約・参照先です。コードはコードのリポジトリに置きます。
サンプルの架空の決定を実案件に混ぜません。補助コマンドは方針を自動作成せず、
プロジェクトの所属を勝手に決めません。

チームで共有する場合は、チームごとに**別の非公開Gitリポジトリ**を作ります。
権限をそのチームだけに与え、差分を確認してcommit/pushします。他のPCではその
リポジトリをcloneしてObsidianで開き、そのPCのパスを設定します。個人scopeは
v0.1ではローカル専用です。この公開キットのリポジトリに実ノートを入れないでください。

チーム管理者が共有repo、scope名、owner、承認済み方針を決めます。メンバーは同じrepoを
自分のPCへcloneします。別の共有履歴を作り直す必要はありません。例：

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

repo名とownerは説明用の仮値です。作成されたTeamフォルダをObsidianで既存Vaultとして開き、
doctor実行前に承認済みの方針ファイルを用意します。任意の個人Vaultにも専用の方針が必要です。

サンプルの `.gitignore` を実データに合わせて確認します。すでに追跡済みのファイルは
ignoreだけでは除外できません。チームで決めた同期方法を使うか、作業開始時の
`git pull --ff-only` と終了時の差分確認・commit/pushを行います。未保存変更や
履歴の分岐でpullできない場合は先に解決します。自動同期・強制pushは提供しません。

## 3. PCごとに設定する

キットのフォルダで実行します。以下はホーム内の設定を書き換えますが、Vault本文は
変更しません。パスと `your-github-organization` は自分の環境に置き換えてください。
ownerにはプロジェクトのGitHub組織名またはユーザー名を指定します。明示的な
所属例外が優先され、親フォルダ名から所属を決めることはしません。

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

方針の既定パスは `Policies/Knowledge policy.md` です。別名ならconfigureに
`--policy '相対パス.md'` を追加します。複数チームはscopeとVaultを分けてconfigureを
繰り返します。個人用が不要なら省略できます。その場合、所属不明の仕事は保存先を
確認し、会社Vaultへ自動的に入れません。ローカル専用のチームには `--local-only` を使います。
個人用は方針を用意してから `--scope personal --vault <personal-vault>` で追加し、
install／doctorを再実行します。仮値は引用符で囲んだ実際のパスに置き換えます。
personalは常にローカル専用です。doctorの期待結果は `PASS local checks`。
方針の欠落やhelper不一致のエラーが残ったまま次へ進みません。

| 項目 | 既定の場所・指定方法 |
|---|---|
| 設定 | `~/.config/obsidian-context/config.json`、`--config` または `OBSIDIAN_CONTEXT_CONFIG` |
| 補助コマンド本体・バックアップ | `~/.local/share/obsidian-context/` |
| 同梱するMIT本文 | `~/.local/share/obsidian-context/LICENSE` |
| 起動コマンド | `~/.local/bin/obsidian-context`、Windowsでは `.cmd` |
| Codex | `~/.codex/AGENTS.md`、`--codex-home` または既存の `CODEX_HOME` |
| Claude Code | `~/.claude/CLAUDE.md`、`--claude-home` または既存の `CLAUDE_CONFIG_DIR` |
| Cursorへ貼り付けるルール | `~/.local/share/obsidian-context/cursor-user-rule.txt` |

隔離したインストール検証には `--home` を使えます。installは管理マーカー内だけを
更新し、ほかの指示を保持します。変更前のファイルはそのままバックアップします。
マーカーの破損はエラーになります。古いマーカーなしルールがある場合は内容を確認し、
必要な場合だけ `--migrate-legacy` を指定します。

## 4. 3ツールで有効にする

- **Codex：** 新しいセッションでAGENTS.mdの読み込みと実動作を確認します。
- **Claude Code：** 新しいセッションでCLAUDE.mdを読み込みます。
- **Cursor：** 設定のRules／User Rules欄に、生成された `cursor-user-rule.txt` の
  内容を貼り付け、古いObsidianルールを置き換えます。画面位置はバージョンで異なります。
  `~/.cursor/rules` のファイルだけではグローバルに有効になりません。デモは
  作業フォルダ内の `.cursor/rules/*.mdc` を使います。同じ全文ルールを重複登録しません。

Cursor用のテキストは、Macでは `open -e "$HOME/.local/share/obsidian-context/cursor-user-rule.txt"`、
PowerShellでは `notepad "$env:USERPROFILE/.local/share/obsidian-context/cursor-user-rule.txt"`
で開けます。画面で保存後、再度開いて全文一致を確認します。日本語回答などの別ルールは保持します。
読込から保存までの検証は新しい**Agent**の会話で行います。Ask／Planの会話は再開後も
読み取り専用のままになる場合があります。

### 日常の呼出し例を更新後も保持する

v0.1.2のinstallerは短い基本ルールを生成します。実環境で確認した呼出し方を明示するため、
次の短い補足をCodexのAGENTS.md、ClaudeのCLAUDE.md、CursorのUser Ruleへ1回ずつ追加します。
英語版と共通の内容です。

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

再installで保全されるよう、`obsidian-context:begin/end` の管理ブロック**外**へ置きます。
既存の所属例外、会議運用、人の注記も管理ブロック外に保管します。この補足や独自の拡張は
installerが自動追加するものではありません。Cursor更新時は生成テキストで基本ルールを
更新し、補足を1つだけ残します。画面へ貼る全文もローカルに保存しておくと確認できます。
章指定は必要な見出しが分かる場合に使い、不明なら初回は省略し、取得結果から選びます。

### 信頼確認と補助コマンドの実行許可

対象の作業フォルダを確認して、通常のWorkspace Trustを承認します。固定した実行ファイル・
helper・configのコマンドだけを許可し、ノートの編集許可とは分けます。既存のdenyを保持します。
helper拒否後に通常Readへ切り替えて正答しても、helper運用の検証は不合格です。
headless／printでは承認画面を表示できず停止する場合があるため、まず対話セッションで
通常の確認を済ませます。検証のために承認機構を無効にしません。

インストール時のPython実行ファイルを使います。WindowsのAI向けコマンドは
PowerShell用です。Pythonの場所が変わったら再インストールします。Workspace Trustや
通常の権限確認を行い、検証のためにセキュリティ確認を無効にしないでください。

**WindowsのClaude Code：** 実際に使う実行ツールを確認します。PowerShell用の許可は
Bash呼出しには適用されません。Bashを使う環境では、同じPython・helper・configを
Bashの引用方法で指定するローカルのコマンド上書きを、Claudeの管理ブロック外だけに追加します。

```text
"<python-executable>" "<installed-helper>" --config "<config-file>" team --compact ...
```

仮値はinstallで表示されたそのPCのパスに置き換え、必要なら区切りを `/` にし、PowerShellの
先頭の `&` を除きます。この固定コマンドだけを許可して、新しい会話の実行履歴を確認します。
Python／Bash／PowerShell全体の許可は不要です。PowerShellを使う他のツールでは生成された
コマンドを使い、helper本体はv0.1.2のままにします。許可の書式は
[Claude公式資料](https://code.claude.com/docs/en/permissions)と
[Cursor CLI公式資料](https://cursor.com/docs/cli/reference/permissions)で確認してください。
アプリとCLIで許可設定が別の場合もあります。

doctorはローカルの設定とコマンドを検査します。Cursorの画面設定、AIの指示遵守、
ログイン、Gitリモートの最新状態は証明しません。[検証手順](verification.ja.md)を
各ツールで実施してください。
**普段のホームとログイン**を使い、検証プロンプトにルール全文を貼らず、架空ノートだけで
確認します。隔離デモの成功だけではグローバルルールが有効になった証明にはなりません。

## 5. 日常の使い方

AIルールにはそのPC用の完全なコマンドが入ります。手動実行も可能です。
Windowsでは `python3` を `py -3` に置き換えます。

```sh
python3 obsidian_context.py team --compact --query 'ノート名'
python3 obsidian_context.py team --compact --file 'Policies/Knowledge policy.md' --file 'Projects/Example.md'
python3 obsidian_context.py team --compact --check 'Policies/Knowledge policy.md=FULL_POLICY_SHA256' --check 'Projects/Example.md=FULL_NOTE_SHA256'
```

ハッシュの仮値には、そのファイルから実際に返った64桁の値を入れます。既知のノートと方針は
1回の呼び出しにまとめます。queryはファイル名検索であり、全文・意味検索ではありません。
一意の完全一致があればそのノートと方針を読み、それ以外は候補名を返します。
必要な候補だけを選びます。広い検索には所属を限定したテキスト検索などを使います。

必要な章が分かっていれば、初回と再開時の両方に同じ `--section '見出し1|見出し2'`
を付けます。[取得範囲の説明](compact-context.md#日本語)も確認してください。

`UNCHANGED` は読んだ内容の再利用、`CONTENT` は更新された抜粋です。
`coverage: partial` は全文を読んだ意味ではありません。必要な未読部分には
`--force --section '見出しパターン'`、または大きな `--chars` を使います。
会話から文脈が失われた場合も再読します。`ERROR`・削除・Git競合を変更なしとして
扱いません。ハッシュはローカルの状態であり、リモートの最新確認は別です。

確定した決定事項は、権限のある編集機能で既存ノートに反映し、変更箇所を一度
確認します。人の注記を保持し、未承認の案や会議発言を承認済みの決定に変えません。

## 6. 更新・解除

この公開リポジトリは新しい履歴から開始しています。以前のリポジトリのチェックアウトや、
Gitが履歴の不一致を報告する場合は、新しいフォルダへ取得して導入し直してください。
ローカル設定・独自ルールは保全し、以前の履歴をこのリポジトリへマージしないでください。


更新前に変更履歴を確認し、ルールをバックアップします。作業ツリーがきれいなキットで
タグをfetchし、対象版（読込負担を減らした版は `v0.1.2`）を選び、installとdoctorを再実行します。
CursorのUser Rulesも更新します。未コミットの変更に上書きで版を切り替えません。
変更履歴とライセンス表記も確認してください。キットは自分や他メンバーのPCを勝手に更新しません。

```sh
git status --short
git fetch origin --tags
git switch --detach v0.1.2
```

最初のコマンドで変更が表示されたら、切り替え前に止めます。管理ブロック内の独自の指示は
バックアップし、install前に外へ移します。各PCで上記の設定・install・doctor・画面登録を
実施し、[日常環境の動作確認](verification.ja.md#日常環境の動作確認)まで行います。
新しい環境で成功するまでバックアップを保持し、復元時は後から行った手修正を上書きしません。
メンバーにはガイドのリンクを共有し、自分のconfig、認証情報、設定バックアップ、ログは渡しません。

解除時はCodex／Claudeの指示ファイルとCursor互換ファイルの
`<!-- obsidian-context:begin -->` から `<!-- obsidian-context:end -->` までだけを
除去し、Cursorの画面でも対応するUser Ruleを削除します。他の指示は残します。
不要になった起動コマンド、本体フォルダ、設定を削除できますが、必要なバックアップは
先に別途保持してください。Vault自体は削除しません。復旧には、その後の手修正を
確認したうえで適切なバックアップを使います。

隔離デモは必要な変更を保管した後、その生成フォルダを削除するだけで解除できます。

## 活用方法を紹介する

自分のREADMEに[Obsidian Agent Kit by UPHASH](https://github.com/UpHash-Network/obsidian-agent-kit)
へのリンクや、[紹介ガイド](branding.md)の任意バッジを載せられます。
元の導入ガイドや更新情報を他の利用者へ伝えられます。画面上の宣伝掲載は任意です。
対象ファイルの再配布時はMITの表記を保持し、公の改善提案には架空の例を使ってください。
[UPHASHについて](https://uphash.net/)

公式資料：[Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md)、
[Claude Code memory](https://code.claude.com/docs/en/memory)、
[Cursor rules](https://cursor.com/docs/rules)。
