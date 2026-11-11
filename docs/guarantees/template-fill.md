# template-fill

| 保証 | 対応テスト |
|---|---|
| `fill_template(mapping, data, output)` は、シートを持たないセル参照（`sheet=None`）の値をアクティブシートに書き込む | `test_fill_template_writes_values` |
| `fill_template` はシート名を持つセル参照の値をそのシートに書き込む | `test_fill_template_writes_values` |
| `fill_template` は書き込んだブックを `output` に保存する | `test_fill_template_writes_values` |
| `fill_template` は `output` を返す | `test_fill_template_writes_values` |
| `fill_template` は、`output` の親ディレクトリが無ければ作ってから保存する | `test_fill_template_writes_values` |
| `data` に `mapping` に無いフィールドがあれば、`"マッピングに存在しない"` を含むメッセージで `FillError` を送出する | `test_fill_template_rejects_unknown_field` |
| `mapping` の必須フィールドが `data` に欠けていれば、`"必須フィールド"` を含むメッセージで `FillError` を送出する | `test_fill_template_rejects_missing_field` |
| `mapping` が参照するシート名がテンプレートに無ければ、`"シート '{シート名}'"` を含むメッセージで `FillError` を送出する | `test_fill_template_rejects_unknown_sheet` |
| テンプレートのファイルが無ければ、`"テンプレートが見つかりません"` を含むメッセージで `FillError` を送出する | `test_fill_template_rejects_missing_template` |
