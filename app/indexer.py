"""ルートA（generated）の生成書類を FTS5 全文検索インデックスへ登録する。

documents.fields_json（Web UI から送信された入力項目の JSON）を
「値のスペース連結テキスト」に変換し、documents_fts へ INSERT する。
"""

import json
import sqlite3


def index_document(conn: sqlite3.Connection, doc_id: int, doc_type: str, fields_json: str) -> None:
    fields: dict[str, str] = json.loads(fields_json)
    content = " ".join(str(value) for value in fields.values())
    conn.execute(
        "INSERT INTO documents_fts (doc_type, content, doc_id) VALUES (?, ?, ?)",
        (doc_type, content, doc_id),
    )
