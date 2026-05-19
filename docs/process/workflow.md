# OverBabel 開発ワークフロー

マスター確認用の記録は **HTML**（`docs/records/`）に集約する。設計の詳細は Markdown でもよいが、**フェーズ完了記録・障害・未解決**は必ず HTML で残す。

## 1 フェーズあたりのサイクル

各 Phase（0〜7、拡張は 8+）で以下を **順に** 行い、完了したら次フェーズへ進む。

| 順 | 作業 | 成果物 | Git |
| --- | --- | --- | --- |
| 1 | **設計** | `docs/records/design/phase-NN-design.md` または `phase-NN-design.html` | 設計のみなら `feature/phase-N-*` でコミット可 |
| 2 | **実装** | `src/` `tests/` 等 | 同一ブランチで継続 |
| 3 | **検証** | `pytest` `ruff` `black` `mypy` | ローカル + CI |
| 4 | **コミット & PUSH** | — | `feature/phase-N-*` → `origin` |
| 5 | **記録** | `docs/records/phase-NN-record.html` を更新 | 記録コミットを同ブランチ or マージ前に追加 |
| 6 | **障害があれば** | `docs/records/issues/resolved/` または `open/` に HTML 1 件ずつ | 解決・未解決を index に反映 |

**マージ**: フェーズ完了後、`main` へ PR → squash merge。必要なら tag（例: `v0.2.0`）。

**Windows コミット**: PowerShell では bash heredoc が使えない。メッセージを `.git/TEMP_COMMIT_MSG.txt` に書き `git commit -F` を使う（[ISSUE-102](../records/issues/resolved/ISSUE-102-powershell-commit-heredoc.html)）。

## 2 記録 HTML の種類

| 種類 | パス | 用途 |
| --- | --- | --- |
| マスター索引 | [docs/records/index.html](../records/index.html) | 全 Phase・全 Issue への入口 |
| フェーズ記録 | `docs/records/phase-NN-record.html` | 設計要約・実装範囲・コミット・検証・未解決リンク |
| 課題（解決済） | `docs/records/issues/resolved/ISSUE-*.html` | 現象・原因・対処・再発防止 |
| 課題（未解決） | `docs/records/issues/open/ISSUE-*.html` | 現象・試したこと・ブロッカー・次アクション |

## 3 Cursor への依頼テンプレ

```
Phase N を workflow.md に従って進めてください。
1. docs/records/design/phase-N-design.md を書く
2. 実装（完了条件: …）
3. pytest / ruff / black / mypy
4. git commit & push (feature/phase-N-*)
5. docs/records/phase-N-record.html を更新
6. 障害があれば issues/ に HTML を追加し index を更新
```

## 4 Phase 一覧（目標）

| Phase | 内容 | 記録 |
| --- | --- | --- |
| 0 | プロジェクト基盤 | [phase-00-record.html](../records/phase-00-record.html) |
| 1 | 透明オーバーレイ MVP | [phase-01-record.html](../records/phase-01-record.html) |
| 2 | キャプチャ + 差分検知 | phase-02-record.html（未） |
| 3 | OCR + 翻訳 | phase-03-record.html（未） |
| 4 | 設定 GUI | phase-04-record.html（未） |
| 5 | gRPC プロセス分離 | phase-05-record.html（未） |
| 6 | 音声字幕 | phase-06-record.html（未） |
| 7 | 配布 | phase-07-record.html（未） |
| 8+ | 拡張（バックログ） | phase-08-backlog.html（未） |

## 5 ブランチ命名

- `feature/phase-N-<short-name>`（例: `feature/phase-2-capture-diff`）
- 記録のみ: `docs/phase-N-records` でも可（実装と同ブランチ推奨）
