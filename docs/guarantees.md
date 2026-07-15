# Guarantee Ledger

## Guarantees

### 1. `tests/template_fill/test_fill.py` — `packages/template_fill/fill.py`（`fill_template`）

- `fill_template(mapping, data, output)` は `data` の各値を `mapping` のセル参照（`sheet=None` はアクティブシート、それ以外は指定シート名）に書き込み、`output` に保存して `output` を返す
- `output` の親ディレクトリが存在しない場合、自動作成してから保存する
- `data` に `mapping` に存在しないフィールドが含まれる場合、`"マッピングに存在しない"` を含むメッセージで `FillError` を送出する
- `mapping` の必須フィールドが `data` に欠けている場合、`"必須フィールド"` を含むメッセージで `FillError` を送出する
- `mapping` が参照するシート名がテンプレートに存在しない場合、`"シート '{シート名}'"` を含むメッセージで `FillError` を送出する
- テンプレートファイルが存在しない場合、`"テンプレートが見つかりません"` を含むメッセージで `FillError` を送出する

| 保証（要約） | 対応テスト |
|---|---|
| 値をセル参照に書き込んで保存し、保存先パスを返す | `test_fill_template_writes_values` |
| 出力先ディレクトリの自動作成 | `test_fill_template_writes_values` |
| マッピングに無いフィールドは `FillError` | `test_fill_template_rejects_unknown_field` |
| 必須フィールド欠落は `FillError` | `test_fill_template_rejects_missing_field` |
| 未知のシート名は `FillError` | `test_fill_template_rejects_unknown_sheet` |
| テンプレート未存在は `FillError` | `test_fill_template_rejects_missing_template` |

### 2. `tests/template_fill/test_mapping.py` — `packages/template_fill/mapping.py`（`load_mapping` / `CellRef`）

- `load_mapping(path)` は YAML の `template` パスを、YAML ファイル自身のディレクトリからの相対パスとして解決し、絶対パスとして `TemplateMapping.template` に格納する
- `load_mapping` は `fields` の各値を `"セル番地"` または `"シート名!セル番地"` の文字列としてパースし、`CellRef(sheet, cell)` に変換する
- `load_mapping` は次のいずれかの場合に `MappingError` を送出する: YAML がマッピング構造でない／`template` キー欠落／`fields` キー欠落／`fields` が空／セル番地の書式が不正／シート名が空文字／フィールド値が文字列でない
- `CellRef.parse` はシート名にスペースを含む表記（例: `"入居 申込!AB12"`）を許容する

| 保証（要約） | 対応テスト |
|---|---|
| `template` パスは YAML ファイル基準で解決 | `test_load_mapping_resolves_template_relative_to_file` |
| `fields` の文字列を `CellRef` にパース | `test_load_mapping_resolves_template_relative_to_file` |
| 不正な YAML（7パターン）は `MappingError` | `test_load_mapping_rejects_invalid` |
| シート名のスペースを許容 | `test_cell_ref_allows_sheet_name_with_space` |

### 3. `tests/watch_convert/test_watcher.py` — `packages/watch_convert/watcher.py`（`is_target` / `PendingQueue` / `watching`）

- `is_target(path, extensions)` は、拡張子が `extensions` に含まれる（大文字小文字を区別しない）かつファイル名が `"~$"` で始まらず `"."` でも始まらない場合に `True` を返す。`extensions` は複数指定にも対応する
- `PendingQueue.mark(path)` は `path` を保留登録し、`debounce_seconds` 経過するまで `pop_ready()` はそれを返さない
- `PendingQueue` は debounce 期間中に同じ `path` が再度 `mark()` されるとタイマーをリセットする
- `PendingQueue.pop_ready()` は静定済みのパスを一度返すと、以降そのパスを再度返さない
- `watching(directory, on_convert, debounce_seconds, poll_interval)` は `directory` 内に対象ファイルが作成・保存されると `on_convert` を呼び出す
- `watching` は `on_convert` が例外を送出しても監視を継続し、他のファイルの変換呼び出しを妨げない
- `watching` は監視対象ディレクトリが存在しない場合 `ValueError` を送出する
- `watching` の `poll_interval` は debounce 完了済みファイルを実際に拾い上げる間隔として使われる（debounce 完了直後ではなく、次の `poll_interval` 到来時に `on_convert` が呼ばれる）

| 保証（要約） | 対応テスト |
|---|---|
| 拡張子（単一・複数）・除外名（ロックファイル/隠しファイル）判定 | `test_is_target`, `test_is_target_multiple_suffixes` |
| debounce: 静定するまで返さない・再markでリセット・返却後は再登場しない | `test_pending_queue_debounces_until_quiet` |
| 新規ファイル検知で `on_convert` を呼ぶ | `test_watching_converts_new_file` |
| `on_convert` の例外後も監視・変換を継続 | `test_watching_survives_converter_error` |
| 存在しないディレクトリは `ValueError` | `test_watching_rejects_non_directory` |
| `poll_interval` がポーリング間隔として使われる | `test_watching_respects_poll_interval` |

### 4. `tests/template_fill/test_cli_template_fill.py` — `packages/template_fill/cli.py`（`main`）

- `main(argv)` は `mapping` YAML と `data` JSON（`-` で標準入力）を読み込み、`fill_template` の結果パスを標準出力に印字して `0` を返す
- `data` JSON のルートがオブジェクトでない場合、標準エラーにメッセージを出し `2` を返す
- `MappingError` / `FillError` / `OSError` / `json.JSONDecodeError` は `"error: {メッセージ}"` として標準エラーに出し `2` を返す

| 保証（要約） | 対応テスト |
|---|---|
| 出力パスを印字し `0` を返す | `test_main_writes_output_and_prints_path` |
| `-` で標準入力からデータを読む | `test_main_reads_data_from_stdin` |
| データのルートがオブジェクトでない場合は `2` | `test_main_rejects_non_object_data` |
| マッピング/フィル系エラーは `error:` 付きで `2` | `test_main_reports_fill_error_and_returns_2` |

### 5. `tests/watch_convert/test_cli_watch_convert.py` — `packages/watch_convert/cli.py`（`main`）

- `main(argv)` は `directory` / `--exec` / `--suffix`（既定 `(".xlsx",)`）/ `--debounce`（既定 `1.0`）を解釈し、そのまま `watching` に渡す
- `watching` に渡す変換関数は、対象パスをカレントディレクトリ基準の相対パスに変換できる場合は相対化した上で、`--exec` の `{src}` を置換したコマンドを `subprocess.run` に渡す
- 監視中に `KeyboardInterrupt` を受けると `0` を返し、監視対象ディレクトリが存在しない場合は `ValueError` を捕捉して `2` を返す

| 保証（要約） | 対応テスト |
|---|---|
| 存在しないディレクトリは `2` | `test_main_returns_2_for_missing_directory` |
| `--suffix` / `--debounce` を `watching` に転送し、`KeyboardInterrupt` で `0` | `test_main_forwards_suffix_and_debounce_and_stops_on_interrupt` |
| 変換関数がパスを相対化し `{src}` を置換してコマンド実行 | `test_convert_relativizes_path_and_runs_command` |

## About

対象は `packages/` 配下の公開関数・例外（`fill_template` / `load_mapping` / `CellRef` / `is_target` / `PendingQueue` / `watching` とその送出例外）と各 `cli.py` の `main`。対象外は `app/` 配下（未着手）・`examples/mansion/` の具体的な中身・外部ライブラリ自体の挙動。**ここに載っていない振る舞いは約束ではなく、予告なく変わりうる。** 地位は design-decisions 相当のドキュメントと同格。
