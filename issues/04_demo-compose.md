## DEMO_MODE 書類シード + docker compose 一発起動
id: 04
branch-slug: demo-compose
github_issue:
status: open
type: feat
対象: docker-compose.yml (新規), Dockerfile (新規), app/seed.py, examples/mansion/seed/documents.json (新規), .env.example
内容: MVP完成条件「docker compose up 一発で DEMO_MODE が立ち上がる」と、空一覧・空検索を防ぐデモ用書類シード
確認: docker compose up でログイン→生成→一覧→検索が到達できること（手動）

---

### 要件

1. `examples/mansion/seed/documents.json`（新規）: 入居申込 3 件・退去届 1 件ぶんの架空フィールドデータ
2. `app/seed.py`: DEMO_MODE 時、上記 JSON から生成パイプライン（Issue 01 の記録 → xlsx → pdf）を通して実生成。pdf 変換失敗（Gotenberg 未起動等）でも xlsx と DB 記録までで続行し、起動を止めない
3. `Dockerfile`（新規）: multi-stage。node で `npm run build` → python イメージに `frontend/dist` + app/ packages/ examples/ を載せ uvicorn 起動
4. `docker-compose.yml`（新規）: `app`（8000 公開、`DEMO_MODE=true`、generated/ shared/ を volume）+ `gotenberg`（gotenberg/gotenberg:8）。GOTENBERG_URL で `http://gotenberg:3000` を注入
5. `.env.example` を compose 変数と揃える

### 制約

- 依存 Issue: 01〜03 すべて（最後に実施）
- 完了後、PLAN.md「MVP の定義」の DoD 1〜5 の動作テスト（WSL2 込み・フェーズ4.1）を user と行い、MVP 完成を判定する
