# Phase 1 設計 — 透明オーバーレイ MVP

## 目的

プライマリモニタ上に透明・クリックスルーの最前面ウィンドウを表示し、トレイとホットキーで制御できることを証明する。

## コンポーネント

| モジュール | 責務 |
| --- | --- |
| `OverBabelApp` | QApplication, overlay/tray/hotkey ライフサイクル |
| `OverlayWindow` | 全画面透明、Phase 1 は `--debug-boxes` 時のみ描画 |
| `OverBabelTray` | コンテキストメニュー、バルーン通知 |
| `HotkeyManager` | pynput `GlobalHotKeys` → Qt シグナルでトグル |

## ウィンドウフラグ

- `FramelessWindowHint`, `WindowStaysOnTopHint`, `Tool`
- `WA_TranslucentBackground`, `WA_TransparentForMouseEvents`, `WA_ShowWithoutActivating`

## 設定

- `%APPDATA%\OverBabel\config.toml` — `hotkey.toggle_overlay` 既定 `<ctrl>+<alt>+t`

## 完了条件

- 透けるオーバーレイ、`Ctrl+Alt+T` トグル、トレイ操作、下のアプリが操作可能
- `--debug-boxes` でモック相当 4 領域表示

## 非スコープ

- 画面キャプチャ、OCR、翻訳、gRPC
