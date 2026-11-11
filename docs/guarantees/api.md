# api

## 書類の一覧と種別

| 保証 | 対応テスト |
|---|---|
| `GET /api/documents` は、未認証（トークン無し）なら `401` を返す | `test_documents_requires_auth` |
| `GET /api/documents` は viewer・editor のどちらのロールにも `200` で一覧を返す | `test_documents_allows_both_roles` |
| `GET /api/documents` は `pdf_path` が NULL の行（PDF が未生成の行）を返さない | `test_documents_returns_only_pdf_ready_rows_with_parsed_fields` |
| `GET /api/documents` の各要素は、`id`・`doc_type`・`fields`・`pdf_path`・`created_at` の5つのキーだけを持つ | `test_documents_returns_only_pdf_ready_rows_with_parsed_fields` |
| `GET /api/documents` の各要素の `fields` は、`fields_json` をパースした dict である | `test_documents_returns_only_pdf_ready_rows_with_parsed_fields` |
| `GET /api/documents` は `created_at` の降順で返す | `test_documents_sorted_by_created_at_desc` |
| `GET /api/documents/types` は、マッピング YAML ごとに拡張子を除いたファイル名を `doc_type` とし、`fields` をマッピングの順で返す | `test_document_types_lists_doc_types_and_field_order` |

## ログインと書類の生成

| 保証 | 対応テスト |
|---|---|
| `POST /api/auth/login` は、正しい資格情報にトークンを発行する | `test_login_issues_token_for_valid_credentials` |
| `POST /api/auth/login` は、誤った資格情報に `401` を返す | `test_login_rejects_invalid_credentials_with_401` |
| `POST /api/generate` は viewer に `403` を返す（editor 限定） | `test_generate_rejects_viewer_with_403` |
| `POST /api/generate` は未知の doc_type に `404` を返す | `test_generate_returns_404_for_unknown_doc_type` |

## 検索と PDF の配信

| 保証 | 対応テスト |
|---|---|
| `GET /api/search` は FTS5 でクエリに一致する書類を返す | `test_search_returns_only_matching_documents_with_pdf` |
| `GET /api/search` は `pdf_path` が NULL の書類を返さない | `test_search_returns_only_matching_documents_with_pdf` |
| `GET /api/files` は `generated` と `shared` の配下の PDF を一覧で返す | `test_files_lists_pdfs_under_generated_and_shared` |
| `GET /api/pdf/{path}` は対象の PDF を `application/pdf` で配信する | `test_pdf_serves_file_as_pdf` |
| `GET /api/pdf/{path}` は対象ディレクトリの外を指すパス（パストラバーサル）を `404` で拒否する | `test_pdf_rejects_path_traversal_with_404` |
