# Phase 0 設計 — プロジェクト基盤

## 目的

開発・CI・パッケージングが可能な最小リポジトリを用意する。

## スコープ

- setuptools (`src/` layout), `overbabel_core`, UI スタブ
- ruff, black, mypy, pytest, pre-commit
- GitHub Actions `ci.yml`
- `docs/architecture.md`, `design-spec.md`, `mockup.html`
- `proto/*.proto` プレースホルダ

## 完了条件

- `git push` 済み、CI 緑
- `python -c "import overbabel_core"` 成功

## 非スコープ

- オーバーレイ実装、キャプチャ、モデル DL
