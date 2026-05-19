# OverBabel

> Realtime screen + audio translation overlay powered by local AI.

OverBabel は、ディスプレイ上の任意のテキストと音声をリアルタイムで指定言語に翻訳し、透明オーバーレイ上に表示するローカル AI ツールです。動画字幕、ゲーム UI、ブラウザ、PDF、Web 会議の音声まで、画面に映る／流れるあらゆる外国語を母国語のまま体験できます。

## 主な特徴

- **完全ローカル動作**：OCR・翻訳・音声認識すべてオフライン推論。クラウド API はオプション。
- **透明クリックスルー**：オーバーレイは常時最前面、下のアプリは普通に操作可能。
- **画面 + 音声の二系統**：画面上の文字（OCR）と音声（Whisper）を同時翻訳。
- **エンジン選択式**：OCR は RapidOCR / Windows OCR / Tesseract、翻訳は Opus-MT / NLLB / LLM、音声は faster-whisper を切替可能。
- **軽量設計**：差分検知 + LRU キャッシュ + INT8 量子化で、CPU のみでも実用速度。

## 動作環境

- Windows 10 / 11（v0.1 時点）
- Python 3.11 以上（CI は 3.11。ローカルは `pyproject.toml` の `requires-python` に従う）
- 最小：CPU 4 コア / RAM 4GB（プロファイル A）
- 推奨：CPU 8 コア / RAM 8GB / 内蔵 GPU（プロファイル B）

## クイックスタート

```powershell
git clone https://github.com/matrix9neonebuchadnezzar2199-sketch/OverBabel.git
cd OverBabel
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,ui]"
python -m overbabel_ui.main
```

初回起動時に翻訳元/先言語を選ぶと、必要モデルが自動 DL されます。

## ドキュメント

- [アーキテクチャ](docs/architecture.md)
- [設計仕様書](docs/design-spec.md)
- [UI モック](docs/mockup.html)
- [開発ワークフロー](docs/process/workflow.md)
- [**開発記録マスター索引（HTML）**](docs/records/index.html) — Phase 進捗・障害・未解決の一覧

## 開発フェーズ

各 Phase は **設計 → 実装 → commit & push → HTML 記録** を繰り返す（[workflow.md](docs/process/workflow.md)）。

| Phase | 内容 | 状態 | 記録 |
| --- | --- | --- | --- |
| 0 | プロジェクト基盤 | 完了 | [record](docs/records/phase-00-record.html) |
| 1 | 透明オーバーレイ MVP | 完了（main 未マージ） | [record](docs/records/phase-01-record.html) |
| 2 | 画面キャプチャ + 差分検知 | 設計済・未実装 | [design](docs/records/design/phase-02-design.md) |
| 3 | OCR + 翻訳パイプライン | 未着手 | — |
| 4 | 設定 GUI 実装 | 未着手 | — |
| 5 | プロセス分離 / gRPC | 未着手 | — |
| 6 | 音声字幕パイプライン | 未着手 | — |
| 7 | 配布パッケージング | 未着手 | — |
| 8+ | 拡張 | バックログ | [backlog](docs/records/design/phase-08-backlog.md) |

## ライセンス

MIT License — [LICENSE](LICENSE) 参照。

OverBabel が利用する各種モデル（NLLB / Opus-MT / Whisper / RapidOCR 等）はそれぞれ独自のライセンスを持つため、配布時は同梱せず初回起動時に DL する方式を採用しています。
