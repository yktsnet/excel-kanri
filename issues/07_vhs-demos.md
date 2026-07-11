## packages の VHS デモ作り直し（示したいこと駆動の構成に）
id: 07
branch-slug: vhs-demos
github_issue: 28
status: close
type: fix
対象: packages/template_fill/demo.tape / packages/watch_convert/demo.tape / packages/template_fill/demo.gif / packages/watch_convert/demo.gif / packages/template_fill/demo/mapping.yaml / packages/template_fill/demo/data.json
内容: 現行の GIF はコマンドを順に打っているだけで、モジュールが何を解決するかが映像として読めない。各 GIF に「示したいこと」を1文で固定し、before/after の対比で見せる構成に作り直す。watch_convert のデモが app/ に依存している矛盾も解消する。
確認: nix-shell --run 'vhs packages/template_fill/demo.tape' / nix-shell --run 'vhs packages/watch_convert/demo.tape' が完走し GIF が更新されること

---

### 現行の問題

- template_fill: `cat` 2連発 + 長い実行コマンドの羅列。「YAML がセル番地と項目名を対応づけ、JSON の値がその番地に着地する」という因果が示されず、流し込み**前**との対比がないため何が起きたか読めない。
- watch_convert: `--exec` に `app.gotenberg` を呼ぶインライン Python（複数行）が画面の主役になっている。「app に依存しない汎用モジュール」のデモが app/ を import しており README の3層構成の主張と矛盾。モジュール固有の価値であるデバウンスも示されていない。

### 示したいこと（各1文・これがデモの背骨）

- **template_fill**: 「マッピング YAML の `セル番地: 項目名` に従い、JSON の値がテンプレート xlsx の該当セルに流し込まれる」
- **watch_convert**: 「ディレクトリへの保存を検知し、連続保存はデバウンスで束ねて、静定後に1回だけ任意コマンドを実行する」

### 要件

**共通**

- ナレーションはコメント行（`Type "# ..."`）で行い、各場面の前に「これから何を見せるか」を1行で示す。
- 実行コマンドは短く保つ。`.venv/bin/python` の直書きをやめ、冒頭で `alias py=.venv/bin/python` を張るなどして本質でない部分を画面から消す。
- 幅・高さ・テーマ等の既存 Set 値は踏襲してよい。全体尺は各30秒以内を目安。

**template_fill**

1. mapping.yaml を表示（demo 用に3項目程度まで刈り込む。`B3: applicant_name` のように番地と項目名の対応が一目で分かる最小形にする。必要なら demo/mapping.yaml・demo/data.json を編集してよい）
2. 流し込み**前**のセル値を表示（B3= None 等。openpyxl のワンライナーは短い形に整える）
3. 実行（1行に収まるコマンド）
4. 流し込み**後**の同じセルを表示し、data.json の値が着地したことを対比で見せる

**watch_convert**

- Gotenberg・app/ を使わない。`--exec 'echo converted: {src}'` のような自己完結のコマンドで「検知→実行」だけを見せる（実変換は app 側の仕事であり、このモジュールの主張は検知とデバウンス）。
1. watcher をバックグラウンド起動（`--debounce` 値を明示）
2. ファイルを1つ置く → 検知ログと exec 出力が出る
3. 同じファイルを短間隔で3回連続保存（`for` ループ等）→ 出力が**1回だけ**であることを見せ、デバウンスを実証する

### 制約

- packages/ 本体のコードは変更しない（デモ素材 demo/ 配下と .tape のみ）。
- README の GIF 参照パスは変わらないため README は触らない。

### user 検証手順（PR の検証手順欄に転記すること）

- 生成された 2 つの demo.gif を再生し、各「示したいこと」の1文が映像から読み取れるか確認する
