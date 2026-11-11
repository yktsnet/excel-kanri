# watcher

## `is_target`

| 保証 | 対応テスト |
|---|---|
| `is_target(path, extensions)` は、拡張子が `extensions` に含まれれば `True` を返す | `test_is_target`, `test_is_target_multiple_suffixes` |
| `is_target` は、拡張子が `extensions` に含まれなければ `False` を返す | `test_is_target`, `test_is_target_multiple_suffixes` |
| `is_target` は拡張子の大文字と小文字を区別しない | `test_is_target`, `test_is_target_multiple_suffixes` |
| `is_target` は、ファイル名が `"~$"` で始まれば `False` を返す | `test_is_target` |
| `is_target` は、ファイル名が `"."` で始まれば `False` を返す | `test_is_target` |
| `is_target` は `extensions` に複数の拡張子を受け付ける | `test_is_target_multiple_suffixes` |

## `PendingQueue`

| 保証 | 対応テスト |
|---|---|
| `PendingQueue.mark(path)` で登録したパスを、`pop_ready()` は `debounce_seconds` が経つまで返さない | `test_pending_queue_debounces_until_quiet` |
| debounce の期間中に同じパスがもう一度 `mark()` されると、`PendingQueue` は待ち時間を数え直す | `test_pending_queue_debounces_until_quiet` |
| `PendingQueue.pop_ready()` は一度返したパスを二度と返さない | `test_pending_queue_debounces_until_quiet` |

## `watching`

| 保証 | 対応テスト |
|---|---|
| `watching(directory, on_convert, ...)` は、`directory` に対象のファイルが作られると、そのファイルについて `on_convert` を呼ぶ | `test_watching_converts_new_file` |
| `watching` は、`on_convert` が例外を送出しても監視を続け、ほかのファイルの `on_convert` を呼ぶ | `test_watching_survives_converter_error` |
| `watching` は、監視するディレクトリが無ければ `ValueError` を送出する | `test_watching_rejects_non_directory` |
| `watching` は debounce を終えたファイルを `poll_interval` ごとに拾う（debounce を終えた直後ではなく、次の `poll_interval` で `on_convert` を呼ぶ） | `test_watching_respects_poll_interval` |
