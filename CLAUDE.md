@context/conventions.md
@context/structure.md

## コマンド

### セットアップ
```
nix-shell   # Python 仮想環境（.venv）に requirements.txt を自動インストール
npm install
```

### 開発
```
uvicorn app.main:app --reload   # バックエンド（:8000）
npm run dev                     # フロントエンド（:5173）
```

### 検証
```
python -m py_compile {.py ファイル}   # Python 構文チェック
npm run typecheck                     # TypeScript 型チェック
npm test                              # フロントエンドテスト
```

## アーキテクチャの要点

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
