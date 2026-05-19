# Phase 2 設計 — 画面キャプチャ + 差分検知

> **状態**: 設計ドラフト（実装前）  
> 記録 HTML: 実装後に `docs/records/phase-02-record.html` を作成する。

## 目的

`dxcam` で画面をキャプチャし、フレーム間差分から ROI（バウンディングボックス）を抽出する。デバッグ時はオーバーレイに赤枠を描画する。

## モジュール案

```
src/overbabel_vision/
  __init__.py
  capture/
    dxcam_capture.py    # 30fps キャプチャループ
  diff/
    frame_diff.py       # numpy 差分 + 連結成分 + bbox リスト
  pipeline.py           # capture → diff → callbacks
```

UI 連携（Phase 2 暫定）:

- `OverlayWindow` に ROI 矩形リストを受け取る API を追加
- `--debug-boxes` 時はダミーではなく **実 ROI** を赤枠描画（色は Phase 1 の `COL_RED_FRAME` を流用）

## データ型（案）

```python
@dataclass(frozen=True)
class RegionOfInterest:
    x: int
    y: int
    w: int
    h: int
    area: int
```

## 設定（仮 → Phase 4 で schema 化）

| キー | 既定 | 説明 |
| --- | --- | --- |
| `capture.fps_cap` | 30 | 上限 FPS |
| `capture.diff_threshold` | 25.0 | グレースケール差分しきい値 |
| `capture.min_roi_area` | 400 | 最小面積 px |

## ベンチ

`scripts/bench.py`:

- 60 秒実行
- 平均 FPS、ROI 数/秒、CPU%、RSS を CSV または stdout

## 完了条件

- 画面変化で赤枠が追従
- `python scripts/bench.py` が 1 分間の統計を出力

## 依存

`pip install -e ".[dev,ui,vision]"` — `dxcam`, `numpy`, `opencv-python-headless`

## リスク・未決

| 項目 | 内容 |
| --- | --- |
| マルチモニタ | Phase 2 はプライマリのみ（Phase 1 と同じ） |
| UI スレッド | キャプチャは QThread or 別スレッド + `pyqtSignal` で ROI 通知 |
| dxcam 未導入環境 | CI はキャプチャ無しの unit test のみ（diff ロジックを numpy 配列でテスト） |

## ブランチ

`feature/phase-2-capture-diff`（`main` マージ後に作成）
