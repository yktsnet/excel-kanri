[🇯🇵 日本語](usage.md) | [🇬🇧 English](usage.en.md)

# Usage

Web App の API 一覧と環境変数、`packages/` 配下の CLI 単体利用。導入の全体像は [README](../README.md) を参照。

## Web App

| 操作 | ロール | エンドポイント |
|---|---|---|
| ログイン | - | `POST /api/auth/login` |
| 書類種別一覧 | viewer / editor | `GET /api/documents/types` |
| 書類生成（xlsx + pdf） | editor のみ | `POST /api/generate` |
| ファイル一覧（generated + shared） | viewer / editor | `GET /api/files` |
| PDF 配信 | viewer / editor | `GET /api/pdf/{path}` |
| 全文検索（ルートAのみ対象） | viewer / editor | `GET /api/search?q=...` |

ルートBは Web UI からの操作を必要としない。`shared/` に Excel を配置・保存すると自動で PDF が更新され、上記の一覧・検索 API に反映される（検索はルートA生成物のみが対象）。

主要な環境変数（詳細は [`.env.example`](../.env.example) 参照）:

| 変数 | 用途 |
|---|---|
| `DEMO_MODE` | `true` でデモ用ログイン画面・シードデータを有効化 |
| `GOTENBERG_URL` | xlsx → pdf 変換を委譲する Gotenberg コンテナの URL |
| `JWT_SECRET` | JWT 署名鍵。本番では `openssl rand -hex 32` 等で生成した値に差し替える |
| `MAPPING_DIR` / `GENERATED_DIR` / `SHARED_DIR` | マッピング YAML・生成物・共有フォルダの配置先 |
| `GEMINI_API_KEY` | 自然言語検索（post-MVP、未実装）用 |

## Package CLIs (`packages/`)

`packages/` 配下の各モジュールは `app/` に依存せず、単体の CLI としても動く。

**`template_fill`** — マッピング YAML + データ JSON から xlsx を生成する。

```bash
python -m packages.template_fill mapping.yaml data.json -o out.xlsx
```

![template_fill demo](../packages/template_fill/demo.gif)

**`watch_convert`** — ディレクトリを監視し、ファイルが静定するたびにコマンドを実行する。

```bash
python -m packages.watch_convert shared/ --exec 'echo converted: {src}'
```

![watch_convert demo](../packages/watch_convert/demo.gif)
