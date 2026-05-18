# OverBabel Architecture

## 1. プロセス構成

OverBabel は 3 プロセスに分離される。

- **overbabel-ui (PyQt6)** — 透明オーバーレイ、設定 GUI、トレイ常駐、ホットキー。
- **overbabel-vision-server** — 画面キャプチャ → 差分検知 → OCR → 翻訳。
- **overbabel-audio-server** — 音声ループバック → VAD → Whisper → 翻訳。

UI ⇄ サーバ間は gRPC ストリーミング（`localhost:7321` / `7322`）。サーバは UI の子プロセスとして起動・終了管理される。

## 2. 画面翻訳パイプライン

`Capture → Diff → ROI 抽出 → OCR → Cache 照合 → Translate → Render`。
キャプチャ層は 30fps で動くが、差分検知で大半のフレームを破棄し、OCR は実質 2〜5fps で十分。LRU 翻訳キャッシュ（xxhash キー）で字幕の繰り返しを吸収する。

## 3. 音声翻訳パイプライン

`Audio Capture (WASAPI Loopback) → Silero VAD → faster-whisper streaming → Translator → Render`。
画面翻訳と Translator を共有することでメモリを節約する。

## 4. 抽象化レイヤ

- `OcrEngine` 基底クラス：`detect(image: np.ndarray) -> list[OcrResult]`
- `Translator` 基底クラス：`translate(texts: list[str], src: str, tgt: str) -> list[str]`
- `AsrEngine` 基底クラス：`transcribe(pcm: np.ndarray, sr: int) -> AsrResult`

新エンジン追加は基底クラスを継承するだけで設定 GUI 側にも自動列挙される。

## 5. 設定永続化

`pydantic v2` で全項目を型定義し、TOML に保存。保存先は `%APPDATA%\OverBabel\config.toml`。
プロファイル A〜D はプリセットとして同梱、個別項目を上書き可能。

## 6. モデル管理

`huggingface_hub.snapshot_download` で `%APPDATA%\OverBabel\models\<engine>\<model_id>\` に格納。
初回起動時にプロファイル選択 → 必要モデル一覧抽出 → 一括 DL（進捗 UI 表示）。
