# mapping

## マッピングの読み込みとセル参照

| 保証 | 対応テスト |
|---|---|
| `load_mapping(path)` は、YAML の `template` のパスを YAML ファイル自身のディレクトリから解決し、絶対パスとして `TemplateMapping.template` に入れる | `test_load_mapping_resolves_template_relative_to_file` |
| `load_mapping` は `fields` の `"セル番地"` の値を `CellRef(sheet=None, cell)` にする | `test_load_mapping_resolves_template_relative_to_file` |
| `load_mapping` は `fields` の `"シート名!セル番地"` の値を `CellRef(sheet, cell)` にする | `test_load_mapping_resolves_template_relative_to_file` |
| `CellRef.parse` はスペースを含むシート名（例: `"入居 申込!AB12"`）を受け付ける | `test_cell_ref_allows_sheet_name_with_space` |

## 不正なマッピング YAML

| 保証 | 対応テスト |
|---|---|
| YAML がマッピングの構造でなければ、`load_mapping` は `MappingError` を送出する | `test_load_mapping_rejects_invalid` |
| `template` キーが無ければ、`load_mapping` は `MappingError` を送出する | `test_load_mapping_rejects_invalid` |
| `fields` キーが無ければ、`load_mapping` は `MappingError` を送出する | `test_load_mapping_rejects_invalid` |
| `fields` が空なら、`load_mapping` は `MappingError` を送出する | `test_load_mapping_rejects_invalid` |
| セル番地の書式が不正なら、`load_mapping` は `MappingError` を送出する | `test_load_mapping_rejects_invalid` |
| シート名が空文字なら、`load_mapping` は `MappingError` を送出する | `test_load_mapping_rejects_invalid` |
| `fields` の値が文字列でなければ、`load_mapping` は `MappingError` を送出する | `test_load_mapping_rejects_invalid` |
