## 機能③ FTS5 全文検索一式（API + UI）
id: 03
branch-slug: search
github_issue: 6
status: close
type: feat
対象: app/indexer.py (新規), app/api/search.py (新規), app/api/generate.py, app/db.py, app/main.py, frontend/src/components/SearchBar.tsx (新規), frontend/src/api/search.ts (新規), frontend/src/App.tsx
内容: ルートAの生成書類を氏名・部屋番号等のキーワードで検索し、プレビューへ飛ぶ縦切り
確認: python -m py_compile {変更 .py 全ファイル} / npm run typecheck

---

### 要件

1. `app/db.py` の `init_db()` に FTS5 仮想テーブル追加: `CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(doc_type, content, doc_id UNINDEXED)`
2. `app/indexer.py`（新規）: `documents` レコードの fields_json を「値のスペース連結テキスト」に変換して `documents_fts` へ INSERT する関数。`app/api/generate.py` の生成成功時に呼ぶ（1行追加）
3. `GET /api/search?q=`（要認証・viewer 以上）: FTS5 MATCH で `{doc_id, doc_type, snippet, pdf_path}` を返す。q 空なら空配列
4. `SearchBar.tsx`: 検索欄 + 結果リスト。結果クリックで Issue 02 のプレビューを開く。`App.tsx` の一覧ペイン上部に配置

### 制約

- 検索対象はルートA（generated）のみ。shared は対象外（PLAN.md 設計方針）
- Gemini 自然言語検索（3.2）は post-MVP。含めない
- 依存 Issue: 01（documents テーブル）、02（プレビュー連携）
