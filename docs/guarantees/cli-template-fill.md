# cli-template-fill

| 保証 | 対応テスト |
|---|---|
| `packages.template_fill` の `main(argv)` は、`mapping` の YAML と `data` の JSON を読み、`fill_template` でセルに書き込んだファイルを出力する | `test_main_writes_output_and_prints_path` |
| `main` は出力したファイルのパスを標準出力に出す | `test_main_writes_output_and_prints_path` |
| `main` は成功すると `0` を返す | `test_main_writes_output_and_prints_path` |
| `main` は、`data` に `-` を渡すと標準入力から JSON を読む | `test_main_reads_data_from_stdin` |
| `main` は、`data` の JSON のルートがオブジェクトでなければ、標準エラーにメッセージを出す | `test_main_rejects_non_object_data` |
| `main` は、`data` の JSON のルートがオブジェクトでなければ `2` を返す | `test_main_rejects_non_object_data` |
| `main` は `FillError` を `"error: {メッセージ}"` として標準エラーに出す | `test_main_reports_fill_error_and_returns_2` |
| `main` は、`FillError` が起きると `2` を返す | `test_main_reports_fill_error_and_returns_2` |
