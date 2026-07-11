## PR記録: feat: ルートA 書類生成 end-to-end（API + 入力UI + Gotenberg連携）
issue: 01 (01_generate.md)
PR: https://github.com/yktsnet/excel-kanri/pull/1
Merged: bd0d2e0e8569df93579f86e523ed47a1ed74bc11

## 変更内容
- `app/config.py`: `gotenberg_url` / `mapping_dir` / `generated_dir` を追加し `.env.example` にも反映
- `app/db.py`: `init_db()` に `documents` テーブル（id, doc_type, fields_json, xlsx_path, pdf_path, created_by, created_at）を追加
- `app/gotenberg.py`（新規）: httpx で Gotenberg の `POST /forms/libreoffice/convert` を呼ぶ `convert_to_pdf(src, dest) -> None`。後続 Issue で `packages.watch_convert` に注入する前提のシグネチャ
- `app/api/generate.py`（新規）:
  - `GET /api/documents/types`: `examples/mansion/mapping/*.yaml` を `packages.template_fill.load_mapping` で走査し種別名・フィールド名一覧を返す（認証必須）
  - `POST /api/generate`: `require_role("editor")` を適用（0.2 の宿題を消化）。`documents` に記録 → `packages.template_fill.fill_template` で xlsx 生成 → `convert_to_pdf` で pdf 変換。変換失敗時は 502 だが SQLite 記録と xlsx は残す（pdf_path は NULL）
- `app/main.py`: `generate_router` を登録
- `requirements.txt`: `httpx==0.28.1` を追加
- `frontend/src/api/documents.ts`（新規）: 上記2エンドポイントのクライアント（`auth.ts` と同じ JWT 付与の流儀）
- `frontend/src/components/DocumentForm.tsx`（新規）: 種別セレクト → フィールド動的生成 → 送信 → 成功/失敗フィードバック（`LoginForm.tsx` と同じ Tailwind 手書き）
- `frontend/src/App.tsx`: ログイン後画面に `DocumentForm` を組み込み。editor ロールのみ表示

## 静的確認結果
- `python -m py_compile app/api/generate.py app/gotenberg.py app/db.py app/config.py app/main.py` → OK
- `npm run typecheck` → OK（エラーなし）
- caller/import 整合性を目視確認: `app/main.py` の router 登録、`app/api/generate.py` の `app.deps` / `app.gotenberg` / `packages.template_fill` の import、`App.tsx` → `DocumentForm.tsx` → `api/documents.ts` の呼び出し連鎖に不整合なし
- `git diff --name-only --cached`:
  .env.example
  app/api/generate.py
  app/config.py
  app/db.py
  app/gotenberg.py
  app/main.py
  frontend/src/App.tsx
  frontend/src/api/documents.ts
  frontend/src/components/DocumentForm.tsx
  requirements.txt

## 検証手順
Gotenberg コンテナは Issue 04 で compose 化されるためこの Issue では未起動。実機確認は Issue 04 完了後に以下で:
1. `DEMO_MODE=true` + Gotenberg 起動状態で `uvicorn app.main:app --reload` / `npm run dev`
2. editor でログイン → 書類種別選択 → フォーム送信 → `generated/` に `.xlsx` + `.pdf` が出ることを確認
3. viewer でログイン → フォームが表示されないこと、および `POST /api/generate` が 403 になることを確認
