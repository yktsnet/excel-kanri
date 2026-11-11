# cli-template-fill

## 成功時の出力

| 保証 | 対応テスト |
|---|---|
| `packages.template_fill` の `main(argv)` は、`mapping` の YAML と `data` の JSON を読み、`fill_template` でセルに書き込んだファイルを出力する | `test_main_writes_output_and_prints_path` |
| `main` は出力したファイルのパスを標準出力に出す | `test_main_writes_output_and_prints_path` |
| `main` は成功すると `0` を返す | `test_main_writes_output_and_prints_path` |
| `main` は、`data` に `-` を渡すと標準入力から JSON を読む | `test_main_reads_data_from_stdin` |

## 失敗時の報告と終了コード

| 保証 | 対応テスト |
|---|---|
| `main` は、`data` の JSON のルートがオブジェクトでなければ、標準エラーにメッセージを出す | `test_main_rejects_non_object_data` |
| `main` は、`data` の JSON のルートがオブジェクトでなければ `2` を返す | `test_main_rejects_non_object_data` |
| `main` は `FillError` を `"error: {メッセージ}"` として標準エラーに出す | `test_main_reports_fill_error_and_returns_2` |
| `main` は、`FillError` が起きると `2` を返す | `test_main_reports_fill_error_and_returns_2` |
| `main` は `MappingError` を `"error: {メッセージ}"` として標準エラーに出す | `test_main_reports_mapping_error_and_returns_2` |
| `main` は、`MappingError` が起きると `2` を返す | `test_main_reports_mapping_error_and_returns_2` |
| `main` は `OSError` を `"error: {メッセージ}"` として標準エラーに出す | `test_main_reports_os_error_and_returns_2` |
| `main` は、`OSError` が起きると `2` を返す | `test_main_reports_os_error_and_returns_2` |
| `main` は `json.JSONDecodeError` を `"error: {メッセージ}"` として標準エラーに出す | `test_main_reports_json_decode_error_and_returns_2` |
| `main` は、`json.JSONDecodeError` が起きると `2` を返す | `test_main_reports_json_decode_error_and_returns_2` |
