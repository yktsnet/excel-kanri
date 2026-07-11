## PR記録: feat: sv6 への CI 自動デプロイ（compose 型）を追加
issue: 06 (06_deploy-sv6.md)
PR: https://github.com/yktsnet/excel-kanri/pull/25
Merged: 99880c83398e1614dfd7657c15d53bbfa977364c

## 変更内容
- docker-compose.yml: app の公開ポートを `${HOST_PORT:-8000}:8000` にパラメータ化。gotenberg のホスト公開ポート（3000）を削除（app からは compose ネットワーク内の http://gotenberg:3000 で到達可能）
- .env.example: `HOST_PORT=8000` を追記
- .github/workflows/ci.yml: `deploy` job を追加（`needs: test` / `if: github.ref == 'refs/heads/main'`）。Tailscale 接続 → ソース同期 → `docker compose up -d --build`。同期先は `~/apps/excel-kanri/`。`.env` / `generated/` / `shared/` は上書きしないよう除外する必要があるため、cicd.md §3-1 のテンプレ（appleboy/scp-action）ではなく burnett01/rsync-deployments（`--exclude=.env --exclude=generated/ --exclude=shared/`）を使用。Secrets は既定の5つ（DEPLOY_HOST / DEPLOY_USER / SSH_PRIVATE_KEY / TS_OAUTH_CLIENT_ID / TS_OAUTH_SECRET）を参照。実値・ドメイン・Tunnel UUID は書いていない

## 静的確認結果
- `nix-shell --run 'python -c "import yaml; yaml.safe_load(open(\".github/workflows/ci.yml\"))"'` → エラーなし
- `docker compose config` → エラーなし。app の ports が `published: "8000"`（HOST_PORT 未設定時のデフォルト）、gotenberg に ports セクションが無いことを確認
- git diff --name-only --cached:
  .env.example
  .github/workflows/ci.yml
  docker-compose.yml

## 検証手順（user）
1. GitHub Secrets 5点を登録（値は secrets-agents/apps.md から流用）
2. sv6: `~/apps/excel-kanri/.env` を配置（`HOST_PORT=<SV6割当ポート>` / `DEMO_MODE=true` / `JWT_SECRET=<生成値>`）
3. sv6: Tunnel ingress + DNS ルート追加 → rebuild（docs-agents/memo/sv6-hosting.md §2）
4. main へマージ → Actions の deploy 成功 → 公開 URL で DEMO ログインできること
