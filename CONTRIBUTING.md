# Contributing to Obsidian Agent Kit

Created and maintained by [UPHASH](https://uphash.net/). Bug reports, documentation
improvements, translations and focused pull requests are welcome in English or
Japanese. Code, rules, guides and fictional samples use the [MIT License](LICENSE).
By intentionally submitting a contribution for inclusion, you agree to provide it
under MIT and confirm you have the right to do so. You retain copyright in your
own contributions. Third-party code needs compatible terms and required notices.
UPHASH logo assets have [separate terms](docs/branding.md).

Include OS, Python version, kit version, AI client version, expected behavior and
a reproduction using the fictional demo. Do not upload real notes, raw chats,
credentials, local configurations, account identifiers or full client logs.
Share a small, manually reviewed excerpt if necessary.
Keep social post drafts and internal launch planning outside this public repository.
The ignore rules and publication audit reject known draft locations even if staged.

Run `python3 -m unittest discover -s tests -v` and `python3 tools/audit_release.py`.
Stage only the intended public files before the audit; it scans Git-tracked files.
The audit complements manual review and does not prove detection of all secrets.
Explain what changed and how you checked it.

## 日本語

[UPHASH](https://uphash.net/)が開発・公開しています。架空デモで再現する不具合、
ガイド改善、翻訳、小さな変更のPRを歓迎します。コード・ルール・ガイド・架空サンプル
への貢献はMITでの提供に同意し、提供する権利がある内容だけを送ってください。
自分の貢献の著作権は保持できます。同梱ロゴの利用条件は別です。
業務ノート・会話ログ・認証情報・PC固有設定は含めず、テストと公開対象の確認を行ってください。
SNS投稿の下書きや内部の公開計画は、この公開リポジトリの外で管理してください。
