## PR記録: feat: ルートAの書類一覧を表形式ビューにし、PDFはオンデマンド表示にする
issue: 10 (10_document-table-view.md)
PR: https://github.com/yktsnet/excel-kanri/pull/37
Merged: c28abd230fc0e310f73d9573efaee0b18c910da4

## 変更内容
中央パネルの既定表示を「ルートAの書類を表形式で見せるテーブル」に変更し、PDFは行クリック等でオンデマンド表示する形にした。左のFileList(PDF一覧)は維持しつつ、テーブルに現れないルートB(共有フォルダ)データを視覚的に強調した。

- `frontend/src/api/documents.ts`: `DocumentRecord` 型と `fetchDocuments(token)` を追加（`GET /api/documents` を呼ぶ。Issue 09で実装済み）
- `frontend/src/components/DocumentTable.tsx`(新規): 書類種別ごとのタブで絞り込み、選択中doc_typeの`fields`順に列ヘッダを出す表形式ビュー。行クリック/「PDFを見る」ボタンで`onSelect`を呼びPDF表示に委譲。空データ時・種別なし時のメッセージ表示
- `frontend/src/App.tsx`: 中央パネルを`selectedFile`の有無で`DocumentTable`/`PdfPreview`に出し分け。`DocumentTable`の行選択・`PdfPreview`の「戻る」操作で`selectedFile`を制御
- `frontend/src/components/PdfPreview.tsx`: 上部操作行に「一覧に戻る」ボタン（`onBack` prop）を追加
- `frontend/src/components/FileList.tsx`: sharedバッジをamberの強調色（背景色+太字+⚠アイコン）にし、generatedをslateの落ち着いた色に変更。sharedの行背景にも薄いamber色を追加して視覚的に区別

## 保証
- ログイン直後の中央パネルの既定表示はテーブルでありPDFではない → `App.tsx`で`selectedFile === null`のとき`DocumentTable`を描画（初期値は`null`）。UIの目視確認で担保（このリポのフロントエンドにテスト基盤は無い）
- テーブルの列はdoc_typeごとに`GET /api/documents/types`の`fields`順で決まり、種別が変われば列構成も切り替わる → `DocumentTable.tsx`で`currentType.fields`をthead/tdの生成元にし、タブ切替で`selectedType`を変えると`currentType`も再計算される。目視確認で担保
- テーブルの行(またはPDFを開く操作)クリックで中央パネルがPDFプレビューに切り替わり、一覧に戻る導線がある → `DocumentTable`の行クリック/「PDFを見る」ボタンが`onSelect`→`setSelectedFile`を呼び、`PdfPreview`の「一覧に戻る」ボタンが`onBack`→`setSelectedFile(null)`を呼ぶ。目視確認で担保
- 左のFileListは既存通りPDFプレビューを開け、ルートB由来項目はルートA項目と視覚的に区別できる → `FileList.tsx`のバッジ色・行背景色をsource別に分岐。目視確認で担保
- 維持する保証: なし（Issue記載通り。このリポの`docs/guarantees.md`は`app/`配下のみを対象とし、フロントエンドの保証記載・テストは現状無い）

## 静的確認結果
- `npm install`（root package.jsonが対象。frontendには別途node_modulesは無い）→ 成功
- `npm run typecheck`（`tsc -b --noEmit`）→ エラーなし
- `npm run build`（`tsc -b && vite build`）→ 成功（45 modules transformed, dist生成）
- コード読解でcaller/importの整合性を確認: `App.tsx`が`DocumentTable`/`PdfPreview`を正しくimportしprops(`onSelect`/`onBack`)を渡している。`DocumentTable.tsx`は`fetchDocumentTypes`/`fetchDocuments`の既存パターンに倣いparseOrThrowを再利用
- `git diff --name-only --cached`:
  frontend/src/App.tsx
  frontend/src/api/documents.ts
  frontend/src/components/DocumentTable.tsx
  frontend/src/components/FileList.tsx
  frontend/src/components/PdfPreview.tsx

## 検証手順
Agent側では以下は未実施（要目視確認）:
1. `nix-shell --run 'uvicorn app.main:app --reload'` でバックエンド起動（`DEMO_MODE=true`推奨）
2. `npm run dev` でフロントエンド起動、ブラウザで editor/viewer それぞれログイン
3. 中央パネルの既定表示がテーブルであることを確認
4. 書類種別タブ切替で列構成が変わることを確認
5. テーブル行クリックでPDFプレビューに切り替わり、「一覧に戻る」でテーブルに戻ることを確認
6. 左FileListでsharedバッジ(⚠共有フォルダ)がgeneratedと視覚的に区別できることを確認
