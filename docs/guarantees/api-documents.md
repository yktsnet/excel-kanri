# api-documents

| 保証 | 対応テスト |
|---|---|
| `GET /api/documents` は、未認証（トークン無し）なら `401` を返す | `test_documents_requires_auth` |
| `GET /api/documents` は viewer・editor のどちらのロールにも `200` で一覧を返す | `test_documents_allows_both_roles` |
| `GET /api/documents` は `pdf_path` が NULL の行（PDF が未生成の行）を返さない | `test_documents_returns_only_pdf_ready_rows_with_parsed_fields` |
| `GET /api/documents` の各要素は、`id`・`doc_type`・`fields`・`pdf_path`・`created_at` の5つのキーだけを持つ | `test_documents_returns_only_pdf_ready_rows_with_parsed_fields` |
| `GET /api/documents` の各要素の `fields` は、`fields_json` をパースした dict である | `test_documents_returns_only_pdf_ready_rows_with_parsed_fields` |
| `GET /api/documents` は `created_at` の降順で返す | `test_documents_sorted_by_created_at_desc` |
