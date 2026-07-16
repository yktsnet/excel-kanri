## PR記録: fix: モバイル幅でのレイアウト崩れを修正する
issue: 08 (08_responsive-layout.md)
PR: https://github.com/yktsnet/excel-kanri/pull/32
Merged: 23c520c9f52728b5b032de157093820a49e92142

## 変更内容
`App.tsx` のファイル一覧/PDFプレビューの2カラムグリッド（`grid-cols-[320px_1fr]`）が固定幅でレスポンシブ対応しておらず、スマホ幅で右側のPDFプレビュー領域が極端に狭くなり崩れる問題を修正した。

- `App.tsx`: 外枠の余白を `p-8` → `p-4 md:p-8` にし、狭幅で余白を減らした
- `App.tsx`: グリッドを `grid-cols-1` を基本とし、`md:grid-cols-[320px_1fr]` で `md` 以上のみ2カラムに切り替えるようにした。あわせて狭幅時にファイル一覧側とPDFプレビュー側へ均等に高さを割り当てるよう `grid-rows-[minmax(0,1fr)_minmax(0,1fr)]` を追加し、`md` 以上では `md:grid-rows-1` で単一行に戻した
- `App.tsx`: `PdfPreview` を `min-h-0` の div でラップし、狭幅の行内で内容が行の高さを押し広げないようにした
- `PdfPreview.tsx`: 未選択時プレースホルダーとiframe表示のルート要素に `min-h-0` を追加し、縦積みレイアウト下でも潰れず表示されるようにした

## 保証
- 新たに宣言する保証: なし（Issue記載の通り、見た目の修正であり明文化して約束する挙動は増えない）
- 維持する保証: なし（`docs/guarantees.md` の対象は `packages/` 配下のみで対象外）。既存のPC幅（1280px相当）でのレイアウトは、変更したクラスがすべて `md:` プレフィックス付きで `md` 以上のブレークポイントでは変更前と同じ値（`grid-cols-[320px_1fr]` / `grid-rows-1` / `p-8`）に解決されるため崩れない

## 静的確認結果
- `npm run typecheck`: 成功（`tsc -b --noEmit` エラーなし）
- `npm run build`: 成功（vite build 完了、44 modules transformed）
- 変更対象は `.py` ファイルなしのため `py_compile` は対象外
- caller/import整合性: `App.tsx` は `PdfPreview` を `min-h-0` の `div` でラップしたのみでprops渡しは変更なし。`PdfPreview.tsx` はクラス名のみの変更でexport/propsのシグネチャは変更なし
- `git diff --name-only --cached`:
  frontend/src/App.tsx
  frontend/src/components/PdfPreview.tsx

## 検証手順
ブラウザでの目視確認（Agent側では実施不可のため、以下はuser/issue-finish側での確認手順）:
1. `npm run dev` でフロントエンドを起動し、`DEMO_MODE=true` でバックエンドも起動する
2. viewer / editor それぞれでログインし、ブラウザのビューポート幅を375px程度まで狭める
3. ファイル一覧とPDFプレビューが横並びから縦積みに切り替わり、プレースホルダー文言・ファイル一覧・PDFプレビューがそれぞれ崩れず表示されることを確認する
4. editor ロールでは追加で「新規作成」ボタンと `GenerateModal` の表示が崩れないことを確認する
5. ビューポート幅を1280px相当に戻し、既存のPCレイアウト（2カラム固定幅320px）が変更前と同じ見た目であることを確認する
