## ルートAの構造化書類一覧APIを追加する
id: 09
branch-slug: documents-api
github_issue:
status: open
type: feat
対象: app/api/generate.py
内容: `fields_json` はすでに構造化データとして保存済みだが、現状これを構造化したまま返すAPIが無く、フロントエンドはPDFを開かないと氏名・部屋番号等の中身を確認できない。ルートA(Web生成)の書類を doc_type・フィールド・PDFパスつきで一覧取得できる `GET /api/documents` を追加し、後続のテーブルビュー実装(Issue 10)の土台にする。

確認: `python -m py_compile app/api/generate.py`。加えて目視確認: `nix-shell --run 'uvicorn app.main:app --reload'` を起動し `curl -H "Authorization: Bearer {token}" http://localhost:8000/api/documents` で doc_type・fields(dict)・pdf_path・created_at を含む配列が返ることを確認する。

---

### 保証
- 新たに宣言する保証:
  - `GET /api/documents` は認証済みユーザー(viewer/editor問わず)が呼べる
  - 返すのは `documents.pdf_path IS NOT NULL`(PDF生成済み)の行のみ。生成失敗でPDF未確定の行は含めない([search.py](../app/api/search.py)の既存ルールと同じ絞り込み)
  - 各要素は `id` / `doc_type` / `fields`(`fields_json` をパースした `dict[str, str]`) / `pdf_path` / `created_at` を含む
  - `created_at` 降順で返す
- 維持する保証:
  - 既存の `/api/documents/types`・`/api/generate`・`/api/files`・`/api/search` のレスポンス仕様は変更しない
  - `docs/guarantees.md` は `app/` 配下を対象外としており、本Issueでの更新は不要

### 詳細

`app/api/generate.py` に以下を追加する(既存の `list_document_types` と同じファイル・同じ認証方式):

```python
class DocumentRecord(BaseModel):
    id: int
    doc_type: str
    fields: dict[str, str]
    pdf_path: str
    created_at: str


@router.get("/documents", response_model=list[DocumentRecord])
def list_documents(current_user: User = Depends(get_current_user)) -> list[DocumentRecord]:
    ...
```

- `db_session()` で `SELECT id, doc_type, fields_json, pdf_path, created_at FROM documents WHERE pdf_path IS NOT NULL ORDER BY created_at DESC` を実行
- `fields_json` は `json.loads()` して `fields` に格納(`generate_document` が `json.dumps(request.fields, ensure_ascii=False)` で保存しているのと対称)
- 認証は `search.py` / `files.py` と同じ `get_current_user`(editor限定にしない。viewerも一覧を見られる必要があるため)
