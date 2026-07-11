## sv6 への CI 自動デプロイ（compose 型）
id: 06
branch-slug: deploy-sv6
github_issue: 26
status: close
type: feat
対象: .github/workflows/ci.yml / docker-compose.yml / .env.example
内容: main マージ後に CI 通過 → sv6 へ自動デプロイする deploy job を追加する（~/dotfiles/docs-agents/cicd.md §3-1 の compose 型）。sv6 では他アプリとポートが衝突するため、compose の公開ポートを環境変数でパラメータ化する。
確認: nix-shell --run 'python -c "import yaml; yaml.safe_load(open(\".github/workflows/ci.yml\"))"' / docker compose config でエラーなし

---

### 要件

**1. docker-compose.yml のポートパラメータ化**

- `app` の `ports` を `"${HOST_PORT:-8000}:8000"` に変更する（ローカルは従来どおり 8000、sv6 では `.env` の `HOST_PORT` で差し替え）。
- `gotenberg` の `ports`（3000 の外部公開）は削除する。app からは compose ネットワーク内の `http://gotenberg:3000` で到達でき、ホスト側に晒す必要がない（sv6 では他アプリとの衝突源になる）。ローカルの DoD 検証にも不要。
- `.env.example` に `HOST_PORT=8000` を追記する。

**2. deploy job の追加（.github/workflows/ci.yml）**

- `~/dotfiles/docs-agents/cicd.md` §3-1 の compose 型に従う: `needs: test`、`if: github.ref == 'refs/heads/main'`。
- Tailscale 接続 → scp でソース同期 → ssh で `docker compose up -d --build`。
- 同期先は `~/apps/excel-kanri/`。rsync/scp は `.env`・`generated/`・`shared/` を上書きしないこと（`.env` は sv6 側で管理。cicd.md §5 の「アプリ別」参照）。
- Secrets 名は既定の5つ: `DEPLOY_HOST` / `DEPLOY_USER` / `SSH_PRIVATE_KEY` / `TS_OAUTH_CLIENT_ID` / `TS_OAUTH_SECRET`（値の登録は user が行う。実値は書かない）。

### 制約

- ワークフロー・コミット・PR 本文にドメイン実値・公開ポート実値・Tunnel UUID を書かない（sv6 の割当ポートは `~/dotfiles/secrets-agents/network.md` で管理する。デバイス名 sv6 は書いてよい）。
- sv6 側の作業（Tunnel ingress 追加・DNS ルート・`.env` 配置・Secrets 登録・Tailscale ACL）は本 Issue の範囲外。ワークフローが参照する前提だけを PR の検証手順に列挙する。

### user 検証手順（PR の検証手順欄に転記すること）

1. GitHub Secrets 5点を登録（値は `secrets-agents/apps.md` から流用）
2. sv6: `~/apps/excel-kanri/.env` を配置（`HOST_PORT=<SV6割当ポート>` / `DEMO_MODE=true` / `JWT_SECRET=<生成値>`）
3. sv6: Tunnel ingress + DNS ルート追加 → rebuild（`docs-agents/memo/sv6-hosting.md` §2）
4. main へマージ → Actions の deploy 成功 → 公開 URL で DEMO ログインできること
