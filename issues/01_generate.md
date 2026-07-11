## 機能① 書類生成一式（API + 入力UI + Gotenberg連携）
id: 01
branch-slug: generate
github_issue: 2
status: close
type: feat
対象: app/api/generate.py (新規), app/gotenberg.py (新規), app/db.py, app/config.py, app/main.py, requirements.txt, .env.example, frontend/src/components/DocumentForm.tsx (新規), frontend/src/api/documents.ts (新規), frontend/src/App.tsx
内容: ルートAを end-to-end で動かす縦切り。Web フォーム入力 → SQLite 記録 → packages.template_fill で xlsx → Gotenberg で pdf → generated/ 保存まで
確認: python -m py_compile {変更 .py 全ファイル} / npm run typecheck

---

### バックエンド要件

1. **書類種別の列挙 `GET /api/documents/types`**: `examples/mansion/mapping/*.yaml` を走査し、種別名（ファイル名 stem）とフィールド名一覧を返す。読み込みは `packages.template_fill.load_mapping` を使う
2. **生成 `POST /api/generate`**
   - body: `{"doc_type": "move-in", "fields": {...}}`
   - `require_role("editor")` を適用（`app/deps.py:36` に実装済み・未使用。0.2 の宿題をここで消化）
   - `documents` テーブルに記録: `id, doc_type, fields_json, xlsx_path, pdf_path, created_by, created_at`（`app/db.py:25` の `init_db()` に CREATE TABLE 追加）
   - `packages.template_fill.fill_template` で `generated/{doc_type}-{id}.xlsx` を生成
   - `app/gotenberg.py`（新規）: httpx で Gotenberg の `POST /forms/libreoffice/convert` に xlsx を送り pdf を保存する `convert_to_pdf(src: Path, dest: Path) -> None`（後続 Issue 02 で watch_convert にも注入するシグネチャ）
   - 変換失敗時は 502 だが SQLite 記録と xlsx は残す（pdf_path は NULL 可）
3. **設定**: `app/config.py` に `gotenberg_url`（既定 `http://localhost:3000`）、`mapping_dir`（既定 `examples/mansion/mapping`）、`generated_dir`（既定 `generated`）。`.env.example` にも追記。httpx を requirements.txt に追加（バージョン固定）

### フロントエンド要件

4. `frontend/src/api/documents.ts`: 上記2エンドポイントのクライアント（JWT 付与は `frontend/src/api/auth.ts` の流儀に合わせる）
5. `DocumentForm.tsx`: 種別セレクト → フィールドを動的生成 → 送信 → 成功/失敗フィードバック。Tailwind 手書き（`LoginForm.tsx` と同じ流儀。shadcn/ui 未導入のまま）
6. `App.tsx`: ログイン後画面に組み込み。**editor のみ表示**（`/api/auth/me` の role で分岐）

### 制約

- `packages/` 配下は変更しない（packages は app を import しない一方向依存）
- Gotenberg 本体はコンテナ前提（Issue 04 で compose 化）。この Issue では起動不要
