# Conventions

## Python
- PEP8 準拠。型アノテーションを付ける（mypy 想定）。
- ファイルは `app/` 配下に配置。
- 外部 API キー・接続情報は `.env` から読む（`.env.example` 参照）。
- `__init__.py` は最小限に留める。

## TypeScript / React
- strict モード有効。`any` 禁止。
- コンポーネントは `src/components/` 配下に配置。
- API クライアントは `src/api/` にまとめる。

## 命名
- Python: snake_case（変数・関数）、PascalCase（クラス）
- TypeScript: camelCase（変数・関数）、PascalCase（コンポーネント・型）
- ファイル: Python は snake_case、TypeScript コンポーネントは PascalCase、その他は camelCase
