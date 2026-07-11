## 機能② 閲覧一式（一覧・PDF配信API + プレビューUI + shared/ 監視）
id: 02
branch-slug: viewer
github_issue:
status: open
type: feat
対象: app/api/files.py (新規), app/api/pdf.py (新規), app/watcher.py (新規), app/main.py, app/config.py, frontend/src/components/FileList.tsx (新規), frontend/src/components/PdfPreview.tsx (新規), frontend/src/api/files.ts (新規), frontend/src/App.tsx
内容: ルートA/B の閲覧を end-to-end で動かす縦切り。ファイル一覧 → PDF プレビュー → 印刷、および watch_convert の app 組み込み（shared/ → PDF 自動更新）
確認: python -m py_compile {変更 .py 全ファイル} / npm run typecheck

---

### API 要件

1. `GET /api/files`（要認証・viewer 以上）: `generated_dir` と `shared_dir` 配下の `.pdf` を `{name, source: "generated"|"shared", path, updated_at}` で列挙（更新日時降順、`~$`・ドットファイル除外）
2. `GET /api/pdf/{path:path}`（要認証・viewer 以上）: `FileResponse`（inline）で配信。**パストラバーサル防止**: resolve 済み実パスが対象 dir 配下であることを検証、外は 404。iframe からの参照になるため Authorization ヘッダに加え `?token=` クエリ認証も受け付ける
3. `app/config.py` に `shared_dir`（既定 `shared`）を追加

### 監視（ルートB）要件

4. `app/watcher.py`（新規）: `packages.watch_convert.watching` に `app/gotenberg.py` の `convert_to_pdf`（同名 `.pdf` 上書き）を注入する薄い層
5. `app/main.py`: `@app.on_event("startup")`（app/main.py:16）を lifespan 方式に置き換え、startup で監視開始・shutdown で停止。`shared_dir` が存在しない場合はログを出してスキップ（起動は失敗させない）。変換失敗時の継続は watching 側で処理済み（packages/watch_convert/watcher.py:96）

### UI 要件

6. `FileList.tsx`: 一覧表示、source をバッジで区別、クリックで選択。`SearchBar`（Issue 03）を後で載せる前提のペイン構成
7. `PdfPreview.tsx`: `<iframe src="/api/pdf/{path}?token=...">` 表示 + 印刷ボタン（`contentWindow.print()`）
8. `App.tsx`: ログイン後メイン画面を一覧+プレビューの2ペインに（viewer / editor 共通）

### 制約

- Excel のダウンロード導線は作らない、PDF 描画はブラウザネイティブのみ（JUDGE.md 2章）
- `packages/` 配下は変更しない
- 依存 Issue: 01（app/gotenberg.py）。実ファイル投入の動作確認は Issue 04 の compose 完成後にまとめて行う
