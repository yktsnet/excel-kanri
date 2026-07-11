## PR記録: fix(vhs): packages の VHS デモを「示したいこと」駆動で作り直す
issue: 07a (07a_vhs-demos-retry.md)
PR: https://github.com/yktsnet/excel-kanri/pull/29
Merged: 9856b1d3a321d7bd9af3116fc1e11e1403a1944e

## 変更内容
現行の GIF はコマンドを順に打っているだけで、モジュールが何を解決するかが
映像として読めなかった。各 GIF に「示したいこと」を1文で固定し、
before/after の対比で見せる構成に作り直した。

- template_fill: mapping.yaml を3項目（customer/item/delivery_date）に刈り込み、
  demo/data.json も対応する3項目に揃えた。流し込み前（B3/B5/B7=None）と
  流し込み後（data.json の値が着地）を対比で見せる構成に変更。
  「マッピングYAMLのセル番地: 項目名に従い、JSONの値がテンプレートxlsxの
  該当セルに流し込まれる」を1文の背骨として全場面をそれに沿わせた。
- watch_convert: app.gotenberg への依存（3層構成と矛盾する app/ import）を排除し、
  `--exec 'echo converted: {src}'` の自己完結コマンドに変更。監視起動
  （--debounce 明示）→ 1ファイル設置で検知・1回実行→ 同一ファイルを0.2秒間隔で
  3回連続保存してもexec実行が1回だけであることを示し、デバウンスを実証する構成にした。
- 共通: `alias py=.venv/bin/python` を冒頭で張り、`.venv/bin/python` の直書きを排除。
  各場面前にナレーション（`Type "# ..."`）を追加。

## 静的確認結果
- git diff --name-only --cached:
  packages/template_fill/demo.gif
  packages/template_fill/demo.tape
  packages/template_fill/demo/data.json
  packages/template_fill/demo/mapping.yaml
  packages/watch_convert/demo.gif
  packages/watch_convert/demo.tape
  → issue の「対象」フィールドと完全一致
- packages/ 本体のコード（fill.py, mapping.py, cli.py, watcher.py）は無変更
- README の GIF 参照パスは変更していない（ファイル名・配置とも従来どおり）

## 検証手順
- `nix-shell --run 'vhs packages/template_fill/demo.tape'` / 同 watch_convert を実行し、
  両方とも正常完了・GIF 更新を確認済み（サンドボックス内では headless Chrome が
  localhost に到達できず失敗したため `dangerouslyDisableSandbox: true` で実行）。
- 生成された GIF をフレーム抽出（ffmpeg fps=1）して目視確認済み:
  - template_fill: mapping.yaml → data.json → 流し込み前(B3=None B5=None B7=None)
    → 実行 → 流し込み後(B3=株式会社サンプル 御中 B5=コピー用紙 A4 B7=2026-07-18)
    の対比が1画面に残る形で表示されることを確認。
  - watch_convert: 監視開始ログ → touch 1回で「実行: echo converted: ...」ログが1回
    → 0.2秒間隔で3回連続touchしても「実行:」ログが1回だけ出力されることを確認（デバウンス実証）。
- user 側でも生成された2つの demo.gif を再生し、各「示したいこと」の1文が
  映像から読み取れるか確認すること（issue 記載の user 検証手順）。
