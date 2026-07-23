## ルートA一覧を構造化データの表ビューにし、PDFはオンデマンド表示にする
id: 10
branch-slug: document-table-view
github_issue:
status: open
type: feat
対象:
  - frontend/src/api/documents.ts
  - frontend/src/components/DocumentTable.tsx (新規)
  - frontend/src/App.tsx
  - frontend/src/components/FileList.tsx
  - frontend/src/components/PdfPreview.tsx
内容: 現状は中央パネルがPDFプレビュー固定で、書類の中身(氏名・部屋番号等)を見るには左のファイル一覧から1件ずつPDFを開くしかなく一覧性が悪い。中央パネルの既定表示を「ルートAの書類を表形式で見せるテーブル」に変え、PDFは行クリック等でオンデマンド表示する形に変更する。左のファイル一覧(PDF一覧)は維持しつつ、テーブルに現れないルートB(共有フォルダ)データを視覚的に強調する。

前提: Issue 09 で追加される `GET /api/documents` に依存する。09が `open`→実装完了してから着手する。

確認: `npm run typecheck` / `npm run build`。加えて目視確認: `npm run dev` + バックエンド起動で、editor/viewer それぞれでログインし、テーブル表示・行クリックでのPDF切替・一覧に戻る導線・書類種別ごとの列切り替え・FileList側のルートB強調表示をブラウザで確認する。

---

### 保証
- 新たに宣言する保証:
  - ログイン直後の中央パネルの既定表示はテーブル(ルートAの書類一覧)であり、PDFではない
  - テーブルの列は書類種別(doc_type)ごとに `GET /api/documents/types` の `fields` 順で決まる。書類種別が異なると列構成も切り替わる(単一の混在テーブルで全種別のフィールドを並べない)
  - テーブルの行(またはその中のPDFを開く操作)をクリックすると中央パネルが該当PDFのプレビューに切り替わり、そこから一覧(テーブル)に戻る導線がある
  - 左のFileList(PDF一覧)は既存通りクリックでPDFプレビューを開ける。加えて、テーブルに現れないルートB(共有フォルダ)由来の項目は、ルートA(生成済み)項目と視覚的に区別できる(バッジ・色・アイコン等)
- 維持する保証: なし(このリポの `docs/guarantees.md` は `app/` 配下を対象外としており、フロントエンドのテスト・保証記載も現状無い。UIの目視確認のみで担保する)

### 詳細

#### `frontend/src/api/documents.ts`
- `DocumentRecord` 型(`id` / `doc_type` / `fields: Record<string, string>` / `pdf_path` / `created_at`)を追加
- `fetchDocuments(token)` を追加し `GET /api/documents` を叩く(既存の `fetchDocumentTypes` と同じ `parseOrThrow` パターンに合わせる)

#### `frontend/src/components/DocumentTable.tsx`(新規)
- `fetchDocumentTypes` で書類種別一覧(doc_type ごとの列定義)を取得し、`fetchDocuments` で書類本体を取得
- 書類種別ごとにタブ(またはドロップダウン)で絞り込み、選択中の doc_type の `fields` 順に列ヘッダを出す。初期選択は先頭の doc_type
- 各行は氏名等のフィールド値 + `created_at` を表示し、行クリック(またはアクション列の「PDFを見る」)で `onSelect` を呼んで親(App.tsx)にPDF表示を委譲する(選択後の遷移先は下記App.tsxの設計に従う)
- 空データ時は「書類がありません」等のメッセージ

#### `frontend/src/App.tsx`
- 中央パネル(現在 `PdfPreview` 固定)を `selectedFile` の有無で出し分ける: `selectedFile === null` なら `DocumentTable`、選択済みなら `PdfPreview`
- `PdfPreview` 側に「一覧に戻る」導線が必要(下記PdfPreview.tsx参照)。戻る操作で `setSelectedFile(null)`
- `DocumentTable` の行クリックは `fields`/`pdf_path` から `FileEntry` 相当(`{ name, source: "generated", path: pdf_path, updated_at: created_at }`)を組み立てて `setSelectedFile` する(既存の `handleGenerated` と同じ組み立て方に合わせる)
- 左サイドバー(新規作成ボタン・SearchBar・FileList)の構成は変更しない

#### `frontend/src/components/FileList.tsx`
- 既存の `SOURCE_BADGE_CLASS` / `SOURCE_LABEL` は generated=緑「生成」、shared=amber「共有」で視覚区別済み。これをベースに、shared(テーブルに現れないルートB)側をより目立たせる方向で調整する(例: アイコン追加・generated側を落ち着いた色にしてsharedを強調色にする、等)。具体的な配色はモダンかつ既存のslate/emerald/amber系トーンから外れない範囲で実装者の裁量とする

#### `frontend/src/components/PdfPreview.tsx`
- 上部の操作行(現在「印刷」ボタンのみ)に「一覧に戻る」ボタンを追加し、`onBack` 等のpropとして親から渡す

### 実装順序
Issue 09(バックエンド)が先。フロントエンドは `GET /api/documents` が存在する前提で実装する。
