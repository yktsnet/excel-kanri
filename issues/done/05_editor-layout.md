## PR記録: fix: editor UI のレイアウト再設計（生成フォームのモーダル化 + 一覧自動更新）
issue: 05 (05_editor-layout.md)
PR: https://github.com/yktsnet/excel-kanri/pull/23
Merged: b8e29d183a72b9a834dbe8d79480be30a0cadd1c

## 変更内容
- editor ログイン時に生成フォームが上段に常時展開され、一覧+プレビューが圧縮される問題を解消。
- 生成フォーム（DocumentForm）をモーダル（新規 GenerateModal.tsx）に移し、editor のみ左ペイン上部に「新規作成」ボタンを表示するようにした。viewer には表示しない。
- DocumentForm に生成成功時の callback prop `onGenerated(result: GenerateResult)` を追加。
- App.tsx で以下を実装:
  1. 生成成功時にモーダルを閉じる
  2. FileList に `refreshSignal` prop を追加し、生成成功のたびにインクリメントして一覧を再取得
  3. `result.pdf_path` から FileEntry を組み立てて選択状態にし、プレビューに表示
- viewer / editor 共通で「左: 検索バー + ファイル一覧、右: PDF プレビュー」の2カラムを全画面の主レイアウトに統一。
- FileList.tsx の `overflow-y-auto`（リスト内部のみのスクロール）は変更なし。

## 静的確認結果
- `npm run typecheck`: 成功（エラーなし）
- `npm run build`: 成功（vite build まで完走、dist 生成確認）
- 対象ファイルとの一致確認: git diff --name-only --cached の出力は以下で issue の「対象」と完全一致
  - frontend/src/App.tsx
  - frontend/src/components/DocumentForm.tsx
  - frontend/src/components/FileList.tsx
  - frontend/src/components/GenerateModal.tsx
- バックエンドは無変更（GenerateResponse の既存フィールドのみ使用）。SearchBar は無変更。

## 検証手順
`docker compose up -d --build` で起動し http://localhost:8000 で:
1. editor でログイン → 一覧+プレビューが全画面2カラムで表示される
2. 「新規作成」→ モーダルでフォーム → 送信 → モーダルが閉じ、一覧に新書類が現れ、プレビューに表示される
3. viewer でログイン → 「新規作成」ボタンが無い
