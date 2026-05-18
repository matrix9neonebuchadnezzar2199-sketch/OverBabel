# OverBabel 設計仕様書（設定項目）

本書は Phase 4 で `overbabel_core/config/schema.py` と PyQt6 設定 GUI に落とし込む対象の一覧です。詳細な既定値・検証ルールは実装時に pydantic で固定します。UI の見た目は [mockup.html](mockup.html) を正とします。

## 共通

- **設定ファイル**: `%APPDATA%\OverBabel\config.toml`
- **スキーマ**: `OverBabelConfig`（pydantic v2）
- **プロファイル**: A / B / C / D（プリセット。個別キーで上書き可）

---

## ページ 1: プロファイル

| 項目 | 型 | 説明 |
| --- | --- | --- |
| `active_profile` | `Literal["A","B","C","D"]` | 現在のプリセット |
| `profiles.*` | ネストオブジェクト | 各プロファイルの CPU/GPU/メモリ方針、既定エンジン参照 |

## ページ 2: 言語

| 項目 | 型 | 説明 |
| --- | --- | --- |
| `source_language` | `str` | 翻訳元（BCP 47 またはアプリ内コード） |
| `target_language` | `str` | 翻訳先 |
| `ui_language` | `str` | 設定 UI の表示言語 |

## ページ 3: キャプチャ（Vision）

| 項目 | 型 | 説明 |
| --- | --- | --- |
| `capture.fps_cap` | `int` | キャプチャ上限 FPS |
| `capture.diff_threshold` | `float` | 差分検知しきい値 |
| `capture.min_roi_area` | `int` | 最小 ROI 面積（px） |
| `capture.monitor_index` | `int` | 対象ディスプレイ（マルチモニタ） |

## ページ 4: 音声

| 項目 | 型 | 説明 |
| --- | --- | --- |
| `audio.device_id` | `str \| None` | ループバックデバイス |
| `audio.sample_rate` | `int` | 入力サンプルレート |
| `audio.vad_aggressiveness` | `float` | VAD 感度 |

## ページ 5: OCR

| 項目 | 型 | 説明 |
| --- | --- | --- |
| `ocr.engine` | `Literal["rapidocr","winocr","tesseract"]` | エンジン選択 |
| `ocr.language_packs` | `list[str]` | 追加言語パック |

## ページ 6: 翻訳

| 項目 | 型 | 説明 |
| --- | --- | --- |
| `translate.engine` | `Literal["opus_mt","nllb","llm_gguf"]` | エンジン選択 |
| `translate.model_id` | `str` | Hugging Face 等のモデル ID |
| `translate.quantization` | `str` | int8 等 |

## ページ 7: モデル

| 項目 | 型 | 説明 |
| --- | --- | --- |
| `models.download_dir` | `path` | キャッシュルート（既定は `get_model_dir()`） |
| `models.auto_update` | `bool` | 起動時の更新チェック |

## ページ 8: オーバーレイ

| 項目 | 型 | 説明 |
| --- | --- | --- |
| `overlay.click_through` | `bool` | クリックスルー |
| `overlay.font_size` | `int` | ベースフォントサイズ |
| `overlay.background_opacity` | `float` | テキスト背景の不透明度 |
| `overlay.text_color` | `str` | `#RRGGBB` |

## ページ 9: プレビュー / デバッグ

| 項目 | 型 | 説明 |
| --- | --- | --- |
| `preview.show_roi_boxes` | `bool` | 差分 ROI の枠表示 |
| `preview.log_fps` | `bool` | FPS ログ |

## ページ 10: パフォーマンス

| 項目 | 型 | 説明 |
| --- | --- | --- |
| `performance.ocr_workers` | `int` | OCR ワーカー数 |
| `performance.translate_workers` | `int` | 翻訳ワーカー数 |
| `performance.cache_size` | `int` | LRU 翻訳キャッシュ最大件数 |

## ページ 11: ホットキー

| 項目 | 型 | 説明 |
| --- | --- | --- |
| `hotkeys.toggle_overlay` | `str` | 既定 `Ctrl+Alt+T` 形式のシリアライズ |
| `hotkeys.open_settings` | `str` | 設定画面 |

---

## 環境変数（`.env`）

`.env.example` を参照。設定ディレクトリ・モデルディレクトリ・gRPC ポートを上書き可能。

## 将来拡張

Phase 8 以降: 字幕帯自動検出、用語辞書、翻訳ログ、対象アプリブラックリスト、インペイント表示、話者分離、他 OS 対応など（`docs/architecture.md` の将来拡張節と同期）。
