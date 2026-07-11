## editor UI のレイアウト再設計（生成フォームのモーダル化 + 生成後の一覧自動更新）
id: 05
branch-slug: editor-layout
github_issue:
status: open
type: fix
対象: frontend/src/App.tsx / frontend/src/components/DocumentForm.tsx / frontend/src/components/FileList.tsx / frontend/src/components/GenerateModal.tsx (新規)
内容: editor ログイン時に縦長の生成フォームが上段に常時展開され、主役であるべき一覧+プレビューが残り高さに圧縮される問題を解消する。生成フォームはモーダルに移し、生成成功後は一覧を自動更新して生成物をプレビューに表示する。
確認: npm run typecheck / npm run build

---

### 現状の問題

1. `App.tsx:60-64` — editor のとき `DocumentForm` が `h-screen` レイアウトの上段に常時展開される。フォームは6項目+ボタンで縦に長く、`App.tsx:66` の一覧+プレビュー領域（`flex-1 min-h-0`）が画面下部に圧縮される。ワイド画面では左右も空白だらけになる。スクロール調整で直る問題ではなく、「たまに使う生成」が「常時使う閲覧・検索」を潰している情報設計の問題。
2. `FileList.tsx:25-29` — ファイル取得が `[token]` 依存のマウント時1回のみ。書類を生成しても一覧に反映されない（再読み込みが必要）。
3. `DocumentForm.tsx:50-52` — 生成成功をテキスト表示するだけで、親に通知する手段（callback prop）がない。

### 要件

- viewer / editor とも「左: 検索バー + ファイル一覧、右: PDF プレビュー」の2カラムを全画面の主レイアウトとする（現在 viewer が見ているレイアウトを editor でも基本にする）。
- editor のみ、左ペイン上部に「新規作成」ボタンを表示する。クリックで `DocumentForm` をモーダル表示する（新規コンポーネント `GenerateModal.tsx` として切り出す。オーバーレイクリックまたは閉じるボタンで閉じられること）。
- `DocumentForm` に生成成功時の callback prop（例: `onGenerated(result: GenerateResponse)`）を追加する。成功時の動作:
  1. モーダルを閉じる
  2. ファイル一覧を再取得する（`FileList` に再取得トリガー prop を追加するか、fetch を `App` に持ち上げるかは実装者判断）
  3. 生成された書類（`result.pdf_path`）を選択状態にしてプレビューに表示する
- viewer には「新規作成」ボタンを表示しない（生成 API は 403 だが UI 上も出さない）。
- 一覧のスクロールは現行どおりリスト内部のみ（`FileList.tsx:34` の `overflow-y-auto` を維持）。ページ全体はスクロールさせない。
- Tailwind 手書きの現行スタイル（slate 系・rounded-lg・shadow-sm）に合わせる。新しい UI ライブラリは導入しない。

### 制約

- バックエンドは変更しない（`GenerateResponse` は `id / doc_type / xlsx_path / pdf_path` を返す。これで足りる）。
- `SearchBar` の挙動は変えない。

### user 検証手順（PR の検証手順欄に転記すること）

`docker compose up -d --build` で起動し http://localhost:8000 で:
1. editor でログイン → 一覧+プレビューが全画面2カラムで表示される
2. 「新規作成」→ モーダルでフォーム → 送信 → モーダルが閉じ、一覧に新書類が現れ、プレビューに表示される
3. viewer でログイン → 「新規作成」ボタンが無い
