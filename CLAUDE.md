@context/conventions.md
@context/structure.md

## フェーズ

**Issueドリブン期**（2026-07-11 に MVP期を終了。汎用モジュール2つの実装で構造が固まったため、残りの MVP 作業は Issue ドリブンで進める）。MVP の定義と完成条件は PLAN.md を参照。

## リポの位置づけ

「既存 Excel 運用に Web 入力・PDF 閲覧・検索を後付けするツールキット」。マンション管理は最初の適用例であり、ドメイン固有物（テンプレート Excel・YAML マッピング・シード）は `examples/mansion/` にのみ置く。`packages/`（汎用モジュール）と `app/`（組み立て）にドメイン語彙を持ち込まない。クライアントの実テンプレートはリポに入れない。

MVP 完成後にリポ全体を public 化する予定。配布形態は「clone して使うリファレンス実装」（PyPI は目指さない）。デモは常設 URL ではなく、各モジュールの VHS GIF（`.tape` を同梱）+ `docker compose` 一発起動で見せる。

## コマンド

### セットアップ
```
nix-shell   # Python 仮想環境（.venv）に requirements.txt を自動インストール
npm install
```

Python 系コマンドは毎回 `nix-shell --run '<コマンド>'` で実行する。Bash ツールは呼び出しごとに新しいシェルになり venv を保持しないため、素の `python3` では ModuleNotFoundError になる。pip を直接叩かない（依存追加は requirements.txt に書き、nix-shell 再入で反映する）。

### 開発
```
uvicorn app.main:app --reload   # バックエンド（:8000）
npm run dev                     # フロントエンド（:5173）
```

### 検証
```
python -m py_compile {.py ファイル}   # Python 構文チェック
python -m pytest                      # packages/ のユニットテスト
npm run typecheck                     # TypeScript 型チェック
npm run build                         # フロントエンドビルド（型チェック込み）
```

## アーキテクチャの要点

3層構成: `packages/`（汎用モジュール。app に依存しない・外部依存は引数で注入）→ `app/`（FastAPI が packages を組み立てる）→ `examples/mansion/`（適用例のテンプレ・マッピング・シード）。

Python FastAPI + SQLite FTS5 がバックエンド。React/Vite（Tailwind CSS + shadcn/ui）のビルド成果物は FastAPI が静的配信する（Nginx 不要）。
PDF変換は Gotenberg コンテナへ HTTP リクエストで委譲する（LibreOffice のサブプロセス管理不要）。

**2つの入力ルート**:
- ルートA: Web UI 入力 → FastAPI → SQLite 記録 → openpyxl でテンプレート生成 → Gotenberg で PDF 変換 → `generated/` に保存
- ルートB: `shared/` フォルダへの Excel 配置・保存 → watchdog 検知 → Gotenberg で PDF 変換（同名上書き）

**認証**: JWT（viewer / editor の2ロール）。`DEMO_MODE=true` でデモ用ログイン画面とシードデータが有効になる。

## 検証手段

PR 前に必ず実施:
1. 変更した `.py` ファイルを `python -m py_compile {file}` で構文確認
2. `.ts` / `.tsx` を変更した場合: `npm run typecheck`
