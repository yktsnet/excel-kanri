@context/conventions.md
@context/structure.md

## コマンド

### セットアップ
```
pip install -r requirements.txt
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

Python FastAPI + SQLite FTS5 がバックエンド。React/Vite のビルド成果物は FastAPI が静的配信する（Nginx 不要）。
ファイル監視（watchdog）→ openpyxl で Excel テンプレート生成 → LibreOffice headless で PDF 変換 → FTS5 インデックス登録、がコアパイプライン。

## 検証手段

PR 前に必ず実施:
1. 変更した `.py` ファイルを `python -m py_compile {file}` で構文確認
2. `.ts` / `.tsx` を変更した場合: `npm run typecheck`
