"""DEMO_MODE 用のシードデータ投入。

- ユーザー: viewer / editor 各1件。
- 書類: examples/mansion/seed/documents.json から、ルートAの生成パイプライン
  （DB記録 → xlsx流し込み → Gotenberg変換 → FTS5インデックス登録）を通して実生成する。
  空の一覧・空の検索結果でデモが始まらないようにするための処理。

Gotenberg 未起動等で PDF 変換が失敗しても、xlsx と DB 記録までで処理を続行し、
アプリの起動自体は止めない（Gotenberg 起動待ちのための短いリトライは行う）。
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.config import settings
from app.db import db_session
from app.gotenberg import GotenbergError, convert_to_pdf
from app.indexer import index_document
from app.security import hash_password
from packages.template_fill import FillError, MappingError, fill_template, load_mapping

logger = logging.getLogger(__name__)

DEMO_USERS = [
    {"email": "viewer@example.com", "password": "demo-viewer", "role": "viewer"},
    {"email": "editor@example.com", "password": "demo-editor", "role": "editor"},
]

SEED_DOCUMENTS_PATH = Path("examples/mansion/seed/documents.json")
SEED_CREATED_BY = "seed@example.com"

_GOTENBERG_WAIT_TIMEOUT_SECONDS = 15.0
_GOTENBERG_WAIT_INTERVAL_SECONDS = 1.0


def seed_demo_data() -> None:
    with db_session() as conn:
        for user in DEMO_USERS:
            conn.execute(
                """
                INSERT OR IGNORE INTO users (email, hashed_password, role)
                VALUES (?, ?, ?)
                """,
                (user["email"], hash_password(user["password"]), user["role"]),
            )
    seed_demo_documents()


def seed_demo_documents() -> None:
    """書類シードを投入する。documents が既に1件でもあれば何もしない（再起動での重複投入を防ぐ）。"""
    with db_session() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM documents").fetchone()
    if row["n"] > 0:
        return

    if not SEED_DOCUMENTS_PATH.is_file():
        logger.warning("シード書類データが見つかりません: %s", SEED_DOCUMENTS_PATH)
        return

    entries = json.loads(SEED_DOCUMENTS_PATH.read_text(encoding="utf-8"))
    if not entries:
        return

    # docker-compose 起動直後は Gotenberg がまだ受け付けられないことがあるため、
    # シード投入前に一度だけ短時間待ち合わせる（タイムアウトしてもそのまま続行する）。
    _wait_for_gotenberg()

    for entry in entries:
        _seed_one_document(entry["doc_type"], entry["fields"])


def _wait_for_gotenberg(
    timeout_seconds: float = _GOTENBERG_WAIT_TIMEOUT_SECONDS,
    interval_seconds: float = _GOTENBERG_WAIT_INTERVAL_SECONDS,
) -> None:
    url = f"{settings.gotenberg_url.rstrip('/')}/health"
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            response = httpx.get(url, timeout=2.0)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(interval_seconds)
    logger.warning("Gotenberg の起動待ちがタイムアウトしました: %s", url)


def _seed_one_document(doc_type: str, fields: dict[str, str]) -> None:
    mapping_path = Path(settings.mapping_dir) / f"{doc_type}.yaml"
    try:
        mapping = load_mapping(mapping_path)
    except MappingError as exc:
        logger.warning("シード書類 '%s' のマッピング読み込みに失敗しました: %s", doc_type, exc)
        return

    created_at = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        cursor = conn.execute(
            """
            INSERT INTO documents (doc_type, fields_json, xlsx_path, pdf_path, created_by, created_at)
            VALUES (?, ?, NULL, NULL, ?, ?)
            """,
            (doc_type, json.dumps(fields, ensure_ascii=False), SEED_CREATED_BY, created_at),
        )
        doc_id = cursor.lastrowid
    assert doc_id is not None

    generated_dir = Path(settings.generated_dir)
    xlsx_path = generated_dir / f"{doc_type}-{doc_id}.xlsx"
    try:
        fill_template(mapping, fields, xlsx_path)
    except FillError as exc:
        logger.warning("シード書類 '%s' の xlsx 生成に失敗しました: %s", doc_type, exc)
        return

    pdf_path = generated_dir / f"{doc_type}-{doc_id}.pdf"
    pdf_saved = False
    try:
        convert_to_pdf(xlsx_path, pdf_path)
        pdf_saved = True
    except GotenbergError as exc:
        logger.warning(
            "シード書類 '%s' の PDF 変換に失敗しました（xlsxは保存済み、起動は継続します）: %s",
            doc_type,
            exc,
        )

    with db_session() as conn:
        conn.execute(
            "UPDATE documents SET xlsx_path = ?, pdf_path = ? WHERE id = ?",
            (str(xlsx_path), str(pdf_path) if pdf_saved else None, doc_id),
        )
        if pdf_saved:
            index_document(conn, doc_id, doc_type, json.dumps(fields, ensure_ascii=False))
