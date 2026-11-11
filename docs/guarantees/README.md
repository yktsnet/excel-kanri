# Guarantee Ledger

このリポが外へ約束している振る舞いと、それを守るテストの一覧である。約束が破れればテストが落ちるので、
ここに書いたことは気づかないうちに実装とずれていかない。**ここに載っていない振る舞いは約束ではなく、予告なく変わりうる**。
対象は `packages/` の公開関数・クラスとその送出例外（`fill_template`・`load_mapping`・`CellRef`・`is_target`・`PendingQueue`・`watching`）、各 `cli.py` の `main`、`app/api/` の HTTP エンドポイントである。`examples/mansion/` の中身、フロントエンドの見た目（目視で確かめる）、外部ライブラリそのものの振る舞いは対象外とする。地位は `docs/design-decisions.md` と同格で、実装と食い違えば指摘の対象になる。

- 目的: いま何を約束しているかを1か所で読む。変更の前に、破ってはいけない約束をここから引く。テストの無い約束を Gaps に残す
- 分け方: 約束の対象（公開 API の群・CLI・HTTP エンドポイント）ごとに1ファイル。テストファイルや Issue の単位では分けない。新しい対象を作ったときだけファイルを足す
- 書き方: 各ファイルに「保証｜対応テスト」の表を1つ置き、1行に約束を1つ、宣言文で書く。表の1行が約束の全文で、表の外に本文を書かない。出典・経緯・設計の理由は書かない（`docs/design-decisions.md` が持つ）。UI の見た目、手で確かめる画面の振る舞い、型検査は載せない。約束が10行以上のファイルは、内容のまとまりで `##` の見出しを立て、見出しごとに表を置く。1つの見出しには3行以上を入れ、3行に満たないまとまりは近い見出しにまとめる。10行未満のファイルには見出しを置かない。見出しは行の主語になる名詞句にし、行に主語が無くても何の約束か分かるようにする。ファイルは分けない
- 引き方: Issue で「維持する保証」を挙げるときは、Issue の対象のファイルを開く。テストが落ちたら、そのテストの名前で台帳を検索すると、破れた約束の行が見つかる。約束が守られていることは、全テストを流して確かめる。コードのファイルから約束を引く仕組みは置かない
- 運用: 変更の前にこの README を読み、変更が触れるファイルから「維持する保証」を引く。約束を足す・変える・消すときは、Issue の保証節で承認を受けた文のまま、該当するファイルの表に行を足す・直す・消し、対応テストも同じ変更で直す。Issue や作業ごとにファイルや節を起こさない。テストの無い約束は Gaps に書き、テストを足したら表へ移す。乖離は `guarantee-audit` で棚卸しする

## Files

| 約束の対象 |
|---|
| [template-fill](template-fill.md) |
| [mapping](mapping.md) |
| [cli-template-fill](cli-template-fill.md) |
| [watcher](watcher.md) |
| [cli-watch-convert](cli-watch-convert.md) |
| [api-documents](api-documents.md) |

## Gaps

- `packages.template_fill` の CLI の `main` が、`MappingError`・`OSError`・`json.JSONDecodeError` を `"error: {メッセージ}"` として標準エラーに出し `2` を返すことが未保証（テストは `FillError` だけを確かめている）
- `packages.watch_convert` の CLI の `main` の既定値（`--suffix` が `(".xlsx",)`、`--debounce` が `1.0`）が未保証
- `packages.watch_convert` の CLI の変換関数が、カレントディレクトリ基準の相対パスにできない対象パスをどう渡すかが未保証
- `watching` が既にあるファイルを保存し直したときに `on_convert` を呼ぶことが未保証（テストは新しく作ったファイルだけを確かめている）
- `POST /api/auth/login` が正しい資格情報でトークンを発行し、誤りで `401` を返すことが未保証
- `GET /api/documents/types` がマッピング YAML から doc_type と `fields` の順を返すことが未保証
- `POST /api/generate` が editor 限定であること（viewer は `403`）と、未知の doc_type に `404` を返すことが未保証
- `GET /api/search` の FTS5 検索の絞り込み（`pdf_path IS NOT NULL` を含む）が未保証
- `GET /api/files` / `GET /api/pdf/{path}` の一覧と PDF の配信（パストラバーサルの拒否を含む）が未保証
