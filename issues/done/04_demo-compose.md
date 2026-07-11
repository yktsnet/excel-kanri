## PR記録: feat: DEMO_MODE 書類シード + docker compose 一発起動
issue: 04 (04_demo-compose.md)
PR: https://github.com/yktsnet/excel-kanri/pull/7
Merged: 81c941ce3cfcc11c7f8cb5936cc726774b6b3508

## 変更内容
- `examples/mansion/seed/documents.json`（新規）: 入居申込3件・退去届1件の架空フィールドデータ。move-in/move-out 各マッピングYAMLのfieldsキーと完全一致させた。
- `app/seed.py`: DEMO_MODE時、上記JSONから既存の生成パイプライン（DB記録 → xlsx流し込み → Gotenberg変換 → FTS5インデックス登録）を通して実書類を生成する `seed_demo_documents()` を追加し、既存の `seed_demo_data()` から呼び出す。
  - documents テーブルが1件でもあれば投入をスキップし、再起動での重複投入を防ぐ。
  - docker compose起動直後はGotenbergがまだ受け付けないことがあるため、投入前に `/health` を最大15秒ポーリングして待ち合わせる（タイムアウトしても続行）。
  - PDF変換失敗時は既存の `POST /api/generate` と同じ方針（xlsxとDB記録のみ残し、FTS5には登録しない）を踏襲し、起動は止めない。
- `Dockerfile`（新規）: multi-stage。`node:22-slim` で `npm install && npm run build` → `python:3.13-slim` に `app/` `packages/` `examples/` と `frontend/dist` を配置し `uvicorn app.main:app` を起動。
- `docker-compose.yml`（新規）: `app`（ポート8000公開、`DEMO_MODE=true`、`generated/` `shared/` をbind volume）+ `gotenberg`（`gotenberg/gotenberg:8`、ポート3000公開）。`GOTENBERG_URL=http://gotenberg:3000` を注入。
- `.env.example`: `SHARED_DIR`（`app/config.py` の `shared_dir` に対応する既存フィールドだが記載漏れだった）を追記し、compose/設定と揃えた。
- `packages/template_fill/demo.tape` / `packages/watch_convert/demo.tape`: 要件6〜8に従い録り直し方針を反映。
  - 冒頭に「これから何を見せるか」の1行コメントを追加。
  - template_fill: 生成実行後、生成したxlsxをopenpyxlで読み返しB3/D5の値をprintする一手を追加（テンプレに値が入った結果を画面に出す）。
  - watch_convert: `--exec` をecho ではなく `app/gotenberg.py` の `convert_to_pdf` を叩くPythonワンライナーに変更し、投入前後の `ls shared/` で xlsx→pdf の出現を映す。Gotenbergコンテナ起動が前提である旨をtapeコメントに明記。

## 静的確認結果
- `python -m py_compile app/seed.py`: OK
- `examples/mansion/seed/documents.json` の各エントリの `fields` キー集合が、対応する `examples/mansion/mapping/{doc_type}.yaml` の `fields` キー集合と完全一致することをスクリプトで確認済み。
- `app/seed.py` のimport・呼び出し先（`app.db` / `app.gotenberg` / `app.indexer` / `app.security` / `packages.template_fill` / `app.config.settings`）は既存シグネチャと整合。呼び出し元 `app/main.py` の `seed_demo_data()` 呼び出しはシグネチャ不変のため変更不要。
- `git diff --name-only --cached` は issue の「対象」フィールドと完全一致:
  ```
  .env.example
  Dockerfile
  app/seed.py
  docker-compose.yml
  examples/mansion/seed/documents.json
  packages/template_fill/demo.tape
  packages/watch_convert/demo.tape
  ```

## 検証手順（実施済み・本ビルダーが確認）
1. `docker build -t excel-kanri-demo-check .` → ビルド成功（frontend build → backend stage、multi-stage とも正常）。
2. `docker run` 単体で `GOTENBERG_URL` を到達不能にした状態で起動 → 約15秒待ち合わせ後にログへ警告を出しつつ起動継続、`GET /api/health` が200を返すことを確認（起動を止めない要件を確認）。
3. `docker compose up -d --build` で `app` + `gotenberg` を同時起動 → `generated/` に move-in 3件・move-out 1件ぶんの `.xlsx` + `.pdf` が実生成されることを確認。
4. `POST /api/auth/login`（editor）→ `GET /api/files`（一覧に4件のPDF）→ `GET /api/search?q=山田`（該当書類がヒット、pdf_path取得）→ `GET /api/pdf/generated/move-in-1.pdf`（200・PDFバイナリ取得）と、DoD 1〜5相当のAPI経路をE2Eで確認。
5. `shared/` にExcelを配置 → `route-b-check.pdf` が自動生成され `GET /api/files` の一覧に反映されることを確認（ルートB）。
6. `docker compose down` でコンテナ・ネットワークを削除し、ビルドしたイメージも削除、検証で作成した `generated/` `shared/` を削除して原状復帰。

## 未実施（本ビルダーの担当外・スコープ外と判断）
- 要件9「GIFを再生成してコミットする」（`vhs packages/<mod>/demo.tape` の実行）は、issueの「対象」フィールドに `demo.gif` が含まれておらず、また `vhs` によるターミナル録画は実行系操作にあたるため、本ビルダーでは実施していません。tape側の変更（要件6〜8）は上記の通り完了・検証済みです。GIF再生成は `issue-finish` 側もしくはuserが手動で `vhs packages/template_fill/demo.tape` / `vhs packages/watch_convert/demo.tape` を実行してコミットしてください。
- PLAN.md「MVPの定義」DoD 1〜5の最終判定（WSL2込み・フェーズ4.1）はuserとの動作テストが前提のため未実施です。上記4/5で相当するAPI経路の自動検証は完了しています。
