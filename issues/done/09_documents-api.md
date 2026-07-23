## PR記録: feat: ルートAの構造化書類一覧APIを追加する
issue: 09 (09_documents-api.md)
PR: https://github.com/yktsnet/excel-kanri/pull/35
Merged: 5616e7a34ca4aa8f43a579a0c896ce58d0eed80a

## 変更内容
`app/api/generate.py` に `GET /api/documents` を追加した。既存の
`list_document_types` と同じファイル・同じ認証方式(`get_current_user`)を
使い、`documents` テーブルから `pdf_path IS NOT NULL`（PDF生成済み）の行を
`created_at` 降順で返す。`fields_json` は `json.loads()` してレスポンスの
`fields: dict[str, str]` に格納する（`generate_document` が
`json.dumps(request.fields, ensure_ascii=False)` で保存しているのと対称）。

## 保証
- `GET /api/documents` は認証済みユーザー(viewer/editor問わず)が呼べる
  → 手動確認: viewer トークンで 200 応答を確認（自動テストなし。ユニット
  テストがないリポ構成のため、既存の `search.py` / `files.py` と同様に
  手動確認のみで対応）
- 返すのは `documents.pdf_path IS NOT NULL` の行のみ
  → 手動確認: DEMO_MODE のシードは Gotenberg 未起動のため全行 `pdf_path`
  が NULL になることを確認した上で、`pdf_path` 設定済みの行を1件手動挿入し、
  その行のみが応答に含まれることを確認した
- 各要素は `id` / `doc_type` / `fields`(dict) / `pdf_path` / `created_at` を含む
  → 手動確認の応答 JSON で全フィールドを確認
- `created_at` 降順で返す
  → SQL の `ORDER BY created_at DESC` で保証（要素1件のためソート順の目視
  確認はできていないが、SQLレベルで担保）
- 維持する保証: `/api/documents/types`・`/api/generate`・`/api/files`・
  `/api/search` は無変更。差分は `app/api/generate.py` への追加のみ
- `docs/guarantees.md` は `app/` 配下を対象外のため更新なし（Issue記載の通り）

## 静的確認結果
- `nix-shell --run 'python -m py_compile app/api/generate.py'` → 成功
- caller/import 整合性: `app/main.py` は既に `generate_router` を
  `include_router` 済みのためルーター登録の変更は不要。
  `Depends(get_current_user)` / `db_session()` / `json` の import は
  ファイル冒頭で既存インポート済み
- `git diff --name-only --cached`: app/api/generate.py

## 検証手順
1. `nix-shell --run 'uvicorn app.main:app --reload'` を起動（DEMO_MODE=true）
2. `POST /api/auth/login` で viewer/editor いずれかのトークンを取得
3. `curl -H "Authorization: Bearer {token}" http://localhost:8000/api/documents`
   で doc_type・fields(dict)・pdf_path・created_at を含む配列が返ることを確認
   （生成済みPDFがない環境では空配列 `[]` が正常応答）
