# システム1 開発計画書 (PLAN.md)

本ドキュメントは「システム1：書類作成自動化 ＋ 資料検索Webアプリ」の開発計画・ロードマップである。

**進捗メモ（2026-07-02）**: フェーズ0のうち 0.1/0.3/0.4 をブートストラップ実装済み（バックエンド `app/`、フロントエンド `frontend/`）。動作確認済み・PR未作成。詳細は各項目のチェック状態を参照。

**進捗メモ（2026-07-11）**: リポの位置づけを「Excel 運用後付けツールキット + 適用例マンション管理」に再定義（CLAUDE.md 参照）。MVP期として汎用モジュール2つを実装完了:

- `packages/template_fill` / `packages/watch_convert`: 実装・pytest 23件パス・CLI 動作確認・VHS デモ GIF 生成済み（`demo.tape` 同梱、再生成は `vhs packages/<mod>/demo.tape`。vhs は home.nix 導入済み）
- `examples/mansion/`: 架空様式テンプレ（move-in / move-out）+ マッピング YAML 作成済み
- 未コミット（このセッションの成果すべて）。コミット粒度は「packages 一式」「examples」「ドキュメント」あたりで分けると読みやすい

同日 **MVP期を終了し Issue ドリブン期へ移行**（構造が固まったため）。残りの MVP 作業は `issues/01〜04` に切り出し済み。実施順は 01_generate → 02_viewer → 03_search → 04_demo-compose（依存順）。04 完了後に DoD 1〜7 を判定し、公開前整備（repo-standardize → repo-readme → readme-i18n → repo-about）へ進む。開発標準は `~/dotfiles/docs-agents/module-guide.md`（module-dev スキル）に一般化済み。

---

## MVP の定義

**「入居申し込み書類を Web フォームから生成でき、共有フォルダに置いた Excel も含めて PDF で閲覧・印刷でき、氏名や部屋番号で過去書類を探せる。これが `docker compose up` + `DEMO_MODE=true` で誰でも即座に体験できる」**

### 完成条件（Definition of Done）

1. `DEMO_MODE=true` で起動 → editor でログイン → 入居申し込みフォーム送信 → `generated/` に `.xlsx` + `.pdf` が出る
2. `shared/` に Excel を保存 → PDF が自動更新され、Web の一覧に出る（WSL2 で Windows からの保存も検知できる）
3. 一覧から PDF をプレビューし、ブラウザ印刷まで到達できる
4. 検索バーに氏名・部屋番号を入れると該当書類がヒットし、プレビューに飛べる
5. viewer ロールでは `POST /api/generate` が 403 になる
6. `packages/` 各モジュールに VHS GIF（`.tape` 同梱）、ルート README に app の画面録画 GIF がある
7. `docker compose up` 一発で DEMO_MODE が立ち上がる

### MVP に含めない（post-MVP）

- Gemini 自然言語検索（3.2）
- デプロイ手順書・Samba 設定（4.2）
- 常設デモ URL（必要になった時点で VPS に DEMO_MODE を置く）
- packages の PyPI 公開（配布は clone して使うリファレンス実装のみ）

---

## 設計方針

### 機能構成

システム1は3つの機能で構成される。実装はフェーズ順に進める。

| # | 機能 | 概要 |
|---|---|---|
| ① | 自動生成 | Web UIで入力 → テンプレートExcel + PDF を自動生成 |
| ② | 閲覧 | ファイル一覧 + PDFプレビュー + 印刷（生成物・共有フォルダ両対応） |
| ③ | 検索 | キーワード + 自然言語（LLM）による書類検索（①の生成物が対象） |

### 入力ルート

**ルートA（Web UIによる書類生成）**

Web UIで書類種別・必要項目を入力する。バックエンドがSQLiteに記録したうえで、テンプレートExcelに値を流し込み `.xlsx` と `.pdf` を自動生成する。生成物は機能②の閲覧・機能③の検索の対象となる。

**ルートB（共有フォルダの監視）**

従業員が共有フォルダ（`shared/`）にExcelを配置・編集・保存すると、`watchdog` が変更を検知して `.pdf` を自動更新する。機能②の閲覧対象だが、機能③の検索対象外とする。

---

## 開発ロードマップ

### フェーズ 0: 認証基盤

全機能の前提となるログイン・権限管理の基盤を構築する。

* [x] **0.1 ユーザーモデルと認証 API**
  * SQLiteに `users` テーブルを追加（`id`, `email`, `hashed_password`, `role`）。→ `app/db.py`
  * `POST /api/auth/login`: メール＋パスワードで認証しJWTを返す。→ `app/api/auth.py`
  * `GET /api/auth/me`: 現在ユーザー情報を返すエンドポイント。→ `app/api/auth.py`
* [ ] **0.2 ロールベースアクセス制御**
  * `viewer`: 閲覧・検索系エンドポイントのみ利用可能。
  * `editor`: viewerの全構限 ＋ `POST /api/generate`を利用可能。
  * `app/deps.py` に `require_role()` は実装済みだが、対象となる editor 限定エンドポイント（`POST /api/generate` 等）がフェーズ1未着手のため未使用。フェーズ1実装時に適用する。
* [x] **0.3 ログインUI**
  * ~~shadcn/uiのFormを使用~~ → 現状は Tailwind 手書きの `LoginForm.tsx`（shadcn/ui未導入）。`frontend/src/components/LoginForm.tsx`
  * `DEMO_MODE=true`時: `viewer` / `editor` タブを表示しデモ認証情報を自動入力する。→ 実装・動作確認済み。
* [x] **0.4 シードデータ**
  * `DEMO_MODE=true`時に投入するデモ用ユーザー（viewer/editor各1件）を用意。→ `app/seed.py`。書類データのシードは未着手（フェーズ1以降で追加）。

### フェーズ 1: ① 自動生成

Web UIからの入力を起点に書類（Excel + PDF）を自動生成するパイプラインを構築する。

* [x] **1.0 汎用モジュール `packages/template_fill`**（2026-07-11 実装。テスト14件 + CLI 動作確認済み）
  * マッピング YAML の読み込み・検証 + openpyxl による流し込み。app に依存しない・ドメイン語彙を含まない。
  * CLI（`python -m packages.template_fill`）と VHS デモ（`demo.tape` + `demo/` アセット）、pytest を含む。
* [ ] **1.1 テンプレートとマッピング定義（適用例）**
  * 架空様式のテンプレートExcel（`.xlsx`）を `examples/mansion/templates/` に配置する。
  * 書類種別と入力フィールド（フィールド名 → セル番地）のマッピングをYAMLで定義する（`examples/mansion/mapping/`）。
* [ ] **1.2 生成API**
  * `POST /api/generate`: フォームデータを受け取り、SQLiteに記録後、`.xlsx` + `.pdf` を `generated/` に保存する。
  * `packages.template_fill` でテンプレートExcelに値を流し込み `.xlsx` を生成する。
  * Gotenberg コンテナへのHTTPリクエストで `.pdf` に変換する（CLAUDE.md参照。LibreOffice headlessサブプロセス管理は不要）。
* [ ] **1.3 書類入力UI**
  * 書類種別の選択メニュー（例：入居申し込み・退去手続き）。
  * 種別ごとの入力フォーム（氏名・部屋番号・入居日等）。
  * 送信後の生成完了フィードバック。

### フェーズ 2: ② 閲覧

生成ファイルと共有フォルダのファイルを統合的に閲覧できるUIとAPIを構築する。

* [ ] **2.1 ファイル一覧API**
  * `GET /api/files`: `generated/`（ルートA）および `shared/`（ルートB）配下のファイル構造を返すAPI。
* [ ] **2.2 PDF配信API**
  * `GET /api/pdf/{path}`: 指定されたPDFをブラウザ向けにストリーム配信するAPI。
* [ ] **2.3 一覧・プレビューUI**
  * ファイル一覧コンポーネント（ルートA・B統合表示）。
  * 選択ファイルのPDFプレビューエリア（iframeまたはブラウザネイティブ）。
  * ブラウザ印刷への導線。
* [ ] **2.4 共有フォルダ監視（ルートB）= 汎用モジュール `packages/watch_convert`**
  * [x] 汎用モジュール部分（2026-07-11 実装。watchdog + デバウンス、変換関数は注入。テスト + CLI 動作確認済み、`demo.tape` あり）
  * [ ] app 側の組み立て: Gotenberg クライアントを注入して `shared/` を監視し `.pdf` を自動更新（同名上書き）。

### フェーズ 3: ③ 検索

ルートAの生成物を対象に、キーワード検索および自然言語検索を実装する。

* [ ] **3.1 全文検索API**
  * `GET /api/search`: SQLite FTS5を用いたキーワード検索API。フェーズ1でSQLiteに記録済みのデータを対象とする。
* [ ] **3.2 自然言語検索（Gemini API）** — post-MVP
  * 自然言語クエリからSQL（FTS5クエリ）を生成するText-to-SQL実装。
  * Gemini APIキーは `.env` から読み込む。
* [ ] **3.3 検索UI**
  * 検索バー + 結果一覧 + PDFプレビュー連携。

### フェーズ 4: テスト・デプロイ検証

* [ ] **4.1 動作テスト**
  * WSL2環境でのエンドツーエンド動作確認（ルートA・B両方）。
  * Windowsからの `shared/` フォルダ操作が `watchdog` に正しく検知されるかテスト。
* [ ] **4.2 デプロイ手順整備** — post-MVP
  * VPS・オンプレLinux向けのセットアップ手順書作成。
  * ルートBの本番運用に必要なSamba設定手順の整備。
