"""FTS5 全文検索 API。

検索対象はルートA（generated）のみ。documents_fts は生成成功時（pdf_path が
確定したタイミング）にのみ登録されるため、documents.pdf_path IS NOT NULL の
行しかヒットしない。
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.db import db_session
from app.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/api", tags=["search"])


class SearchResult(BaseModel):
    doc_id: int
    doc_type: str
    snippet: str
    pdf_path: str


@router.get("/search", response_model=list[SearchResult])
def search_documents(q: str = "", current_user: User = Depends(get_current_user)) -> list[SearchResult]:
    query = q.strip()
    if not query:
        return []

    # FTS5 の特殊構文（"-", "*", 二重引用符等）による MATCH 構文エラーを避けるため、
    # クエリ全体を1つのフレーズとして扱う。
    escaped = query.replace('"', '""')
    match_expr = f'"{escaped}"'

    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT documents_fts.doc_id AS doc_id,
                   documents_fts.doc_type AS doc_type,
                   snippet(documents_fts, 1, '[', ']', '...', 8) AS snippet,
                   documents.pdf_path AS pdf_path
            FROM documents_fts
            JOIN documents ON documents.id = documents_fts.doc_id
            WHERE documents_fts MATCH ?
              AND documents.pdf_path IS NOT NULL
            ORDER BY rank
            """,
            (match_expr,),
        ).fetchall()

    return [
        SearchResult(
            doc_id=row["doc_id"],
            doc_type=row["doc_type"],
            snippet=row["snippet"],
            pdf_path=row["pdf_path"],
        )
        for row in rows
    ]
