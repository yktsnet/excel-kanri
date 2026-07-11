## PR記録: feat: FTS5 全文検索一式（API + UI）
issue: 03 (03_search.md)
PR: https://github.com/yktsnet/excel-kanri/pull/5
Merged: a41b8d4c3d4cc91783c1f52142937303f1f03423

## 変更内容
- `app/db.py`: `init_db()` に FTS5 仮想テーブル `documents_fts`（doc_type, content, doc_id UNINDEXED）を追加
- `app/indexer.py`（新規）: `documents.fields_json` を値のスペース連結テキストに変換し `documents_fts` へ INSERT する `index_document()`
- `app/api/generate.py`: 書類生成成功時（PDF変換まで成功した場合のみ）に `index_document()` を呼びインデックス登録
- `app/api/search.py`（新規）: `GET /api/search?q=`（要認証・viewer 以上）。FTS5 MATCH で `{doc_id, doc_type, snippet, pdf_path}` を返す。q が空なら空配列。クエリ全体をフレーズとしてエスケープしMATCH構文エラーを回避
- `app/main.py`: search ルーターを登録
- `frontend/src/api/search.ts`（新規）: `searchDocuments()` クライアント
- `frontend/src/components/SearchBar.tsx`（新規）: 検索欄 + 結果リスト。結果クリックで検索結果を `FileEntry` に変換し `onSelect` を呼ぶ（Issue 02 の PdfPreview を開く）
- `frontend/src/App.tsx`: 一覧ペイン（FileList）の上部に SearchBar を配置

## 静的確認結果
- `python -m py_compile app/indexer.py app/api/search.py app/api/generate.py app/db.py app/main.py` → OK
- `npm run typecheck` → OK（エラーなし）
- caller/import 整合性を目視確認: generate.py からの `index_document` 呼び出し、main.py への search_router 登録、SearchBar.tsx / App.tsx の import パスと props の受け渡し
- `git diff --name-only --cached`:
  - app/api/generate.py
  - app/api/search.py
  - app/db.py
  - app/indexer.py
  - app/main.py
  - frontend/src/App.tsx
  - frontend/src/api/search.ts
  - frontend/src/components/SearchBar.tsx
  （issue「対象」フィールドと完全一致）

## 検証手順
1. `uvicorn app.main:app --reload` と `npm run dev` を起動
2. ルートAで書類を1件生成（PDF変換まで成功させる）
3. 検索欄に生成時に入力した氏名や部屋番号を入力して検索し、結果が表示されることを確認
4. 結果をクリックし、右ペインに該当PDFのプレビューが開くことを確認
5. 未認証（トークンなし）で `GET /api/search?q=...` を叩き 401 になることを確認
