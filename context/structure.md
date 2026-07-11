# Structure

## 3層構成

- `packages/`: 汎用モジュール。app に依存せず、ドメイン語彙（マンション・入居等）を含まない。外部依存（Gotenberg・パス・時刻）は引数で注入する
- `app/`: FastAPI + React。packages を組み立てた Web アプリ（これも汎用）
- `examples/mansion/`: 適用例。マンション管理のテンプレート Excel・YAML マッピング・シードデータはここにのみ置く

## ディレクトリ構成（予定）

```
excel-kanri/
├── packages/               # 汎用モジュール（app を import しない）
│   ├── template_fill/      # YAML マッピング + データ → openpyxl で xlsx 生成
│   │   ├── mapping.py      # マッピング YAML の読み込み・検証
│   │   ├── fill.py         # テンプレート流し込み
│   │   ├── cli.py          # python -m packages.template_fill（VHS デモ対象）
│   │   └── demo.tape       # VHS デモスクリプト
│   └── watch_convert/      # ディレクトリ監視 → 変換関数（注入）実行
│       ├── watcher.py      # watchdog によるファイル監視 + デバウンス
│       ├── cli.py          # python -m packages.watch_convert（VHS デモ対象）
│       └── demo.tape
├── tests/                  # packages/ のユニットテスト（pytest。src をミラー）
├── app/                    # Python バックエンド（FastAPI）
│   ├── main.py             # エントリポイント・ルーター登録
│   ├── gotenberg.py        # Gotenberg クライアント（packages へ注入する変換関数）
│   ├── indexer.py          # SQLite FTS5 インデックス管理（ルートA）
│   └── api/                # FastAPI ルーター
│       ├── auth.py         # POST /api/auth/login, GET /api/auth/me
│       ├── generate.py     # POST /api/generate（書類生成。editor 限定）
│       ├── files.py        # GET /api/files（ファイル一覧）
│       ├── pdf.py          # GET /api/pdf/{path}（PDF ストリーム配信）
│       └── search.py       # GET /api/search（FTS5 検索）
├── frontend/               # React + Vite
│   ├── src/
│   │   ├── components/
│   │   └── api/
│   └── dist/               # ビルド成果物（gitignore）
├── examples/
│   └── mansion/            # マンション管理の適用例（架空様式のみ。実テンプレは置かない）
│       ├── templates/      # 書類種別ごとのテンプレート Excel
│       ├── mapping/        # 書類種別ごとのフィールド→セルマッピング（YAML）
│       └── seed/           # DEMO_MODE 用シードデータ
├── generated/              # ルートA の生成物（.xlsx / .pdf。gitignore）
├── shared/                 # ルートB の共有フォルダ（watchdog 監視対象。gitignore）
├── docker-compose.yml      # app + Gotenberg（DEMO_MODE 一発起動）
├── requirements.txt
├── package.json
└── .env.example
```

## データフロー

### ルートA（Web UI → 書類自動生成）

1. 従業員が Web UI から書類種別・入力項目を送信
2. FastAPI が SQLite にデータを記録
3. `examples/mansion/mapping/` の YAML に従い `packages.template_fill` がテンプレート Excel に値を流し込み → `generated/` に `.xlsx` 保存
4. Gotenberg で `.pdf` に変換し `generated/` に保存
5. Web UI → `GET /api/files` → 一覧表示 → `GET /api/pdf/{path}` → PDFプレビュー・印刷

### ルートB（共有フォルダ → PDF自動更新）

1. 従業員の Windows PC → `shared/` フォルダへ Excel を配置・保存（本番は Samba 経由）
2. `packages.watch_convert` が変更（`IN_CLOSE_WRITE`）を検知
3. 注入された変換関数（Gotenberg クライアント）が `.pdf` を自動更新（同名上書き）
4. Web UI → `GET /api/files` → 一覧表示 → `GET /api/pdf/{path}` → PDFプレビュー・印刷
