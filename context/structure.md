# Structure

## ディレクトリ構成（予定）

```
excel-kanri/
├── app/                    # Python バックエンド（FastAPI）
│   ├── main.py             # エントリポイント・ルーター登録
│   ├── watcher.py          # watchdog によるファイル監視（ルートB）
│   ├── generator.py        # openpyxl テンプレート流し込み・LibreOffice PDF変換
│   ├── indexer.py          # SQLite FTS5 インデックス管理（ルートA）
│   └── api/                # FastAPI ルーター
│       ├── generate.py     # POST /api/generate（書類生成）
│       ├── files.py        # GET /api/files（ファイル一覧）
│       ├── pdf.py          # GET /api/pdf/{path}（PDF ストリーム配信）
│       └── search.py       # GET /api/search（FTS5 検索）
├── frontend/               # React + Vite
│   ├── src/
│   │   ├── components/
│   │   └── api/
│   └── dist/               # ビルド成果物（gitignore）
├── templates/              # 書類種別ごとのテンプレートExcel
├── mapping/                # 書類種別ごとのフィールド→セルマッピング（YAML）
├── generated/              # ルートA の生成物（.xlsx / .pdf）
├── shared/                 # ルートB の共有フォルダ（watchdog 監視対象）
├── requirements.txt
├── package.json
└── .env.example
```

## データフロー

### ルートA（Web UI → 書類自動生成）

1. 従業員が Web UI から書類種別・入力項目を送信
2. FastAPI が SQLite にデータを記録
3. `mapping/` の YAML に従い `openpyxl` でテンプレートExcelに値を流し込み → `generated/` に `.xlsx` 保存
4. LibreOffice headless で `.pdf` に変換し `generated/` に保存
5. Web UI → `GET /api/files` → 一覧表示 → `GET /api/pdf/{path}` → PDFプレビュー・印刷

### ルートB（共有フォルダ → PDF自動更新）

1. 従業員の Windows PC → `shared/` フォルダへ Excel を配置・保存（本番は Samba 経由）
2. `watchdog` が `IN_CLOSE_WRITE` イベントを検知
3. LibreOffice headless で `.pdf` を自動更新（同名上書き）
4. Web UI → `GET /api/files` → 一覧表示 → `GET /api/pdf/{path}` → PDFプレビュー・印刷
