# cli-watch-convert

| 保証 | 対応テスト |
|---|---|
| `packages.watch_convert` の `main(argv)` は、`directory` をそのまま `watching` に渡す | `test_main_forwards_suffix_and_debounce_and_stops_on_interrupt` |
| `main` は `--suffix` の値を `watching` に渡す | `test_main_forwards_suffix_and_debounce_and_stops_on_interrupt` |
| `main` は `--debounce` の値を `watching` に渡す | `test_main_forwards_suffix_and_debounce_and_stops_on_interrupt` |
| `main` は、`--suffix` を指定しなければ `(".xlsx",)` を `watching` に渡す | `test_main_defaults_suffix_and_debounce` |
| `main` は、`--debounce` を指定しなければ `1.0` を `watching` に渡す | `test_main_defaults_suffix_and_debounce` |
| `main` は、監視中に `KeyboardInterrupt` を受けると `0` を返す | `test_main_forwards_suffix_and_debounce_and_stops_on_interrupt` |
| `main` は、監視するディレクトリが無ければ `2` を返す | `test_main_returns_2_for_missing_directory` |
| `main` が `watching` に渡す変換関数は、対象のパスをカレントディレクトリ基準の相対パスにする | `test_convert_relativizes_path_and_runs_command` |
| `main` が `watching` に渡す変換関数は、`--exec` の `{src}` をそのパスに置き換えたコマンドを `subprocess.run` で実行する | `test_convert_relativizes_path_and_runs_command` |
