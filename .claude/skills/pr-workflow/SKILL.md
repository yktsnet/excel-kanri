---
name: pr-workflow
description: ブランチ作成 → 実装 → 検証 → PR 作成の一連フロー
---

# PR Workflow

1. `git checkout -b claude/{id}-{slug}` でブランチ作成
2. Issue の `対象:` に列挙されたファイルを編集
3. **検証**（PR 作成前に必ず実施）:
   - 変更した `.py` ファイルを `python -m py_compile {file}` で構文確認
   - `.ts` / `.tsx` を変更した場合: `npm run typecheck`
4. `gh pr create` で PR 作成
   - `## 検証手順` には Agent 側で確認できない操作（手動テスト・動作確認）を記載し、user に委ねる
