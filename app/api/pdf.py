"""PDF 配信 API。

iframe の src からの参照になるため、Authorization ヘッダに加えて
`?token=` クエリでの認証も受け付ける（app/deps.py の get_current_user は
ヘッダのみのため、ここでは同等のロジックを直接持つ）。
パストラバーサル防止のため、resolve 済み実パスが対象ディレクトリ配下であることを検証する。
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse

from app.config import settings
from app.db import db_session
from app.models import User
from app.security import decode_access_token

router = APIRouter(prefix="/api", tags=["pdf"])

_SOURCE_DIRS = {
    "generated": lambda: Path(settings.generated_dir),
    "shared": lambda: Path(settings.shared_dir),
}

_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ファイルが見つかりません")


def _authenticate(request: Request, token: str | None) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        raw_token = auth_header.split(" ", 1)[1]
    elif token:
        raw_token = token
    else:
        raise credentials_error

    payload = decode_access_token(raw_token)
    if payload is None:
        raise credentials_error

    email = payload.get("sub")
    if email is None:
        raise credentials_error

    with db_session() as conn:
        row = conn.execute("SELECT id, email, role FROM users WHERE email = ?", (email,)).fetchone()
    if row is None:
        raise credentials_error

    return User(id=row["id"], email=row["email"], role=row["role"])


@router.get("/pdf/{path:path}")
def get_pdf(path: str, request: Request, token: str | None = None) -> FileResponse:
    _authenticate(request, token)

    source, _, relative = path.partition("/")
    if source not in _SOURCE_DIRS or not relative:
        raise _NOT_FOUND

    base_dir = _SOURCE_DIRS[source]().resolve()
    target = (base_dir / relative).resolve()

    if target.suffix.lower() != ".pdf" or not target.is_relative_to(base_dir) or not target.is_file():
        raise _NOT_FOUND

    return FileResponse(target, media_type="application/pdf", content_disposition_type="inline")
