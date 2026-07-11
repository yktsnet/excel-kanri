"""ファイル一覧 API。

ルートA（generated_dir）とルートB（shared_dir）配下の PDF をまとめて列挙する。
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import settings
from app.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/api", tags=["files"])

Source = Literal["generated", "shared"]


class FileEntry(BaseModel):
    name: str
    source: Source
    path: str
    updated_at: str


def _is_visible(path: Path) -> bool:
    """Office のロックファイル（~$*）や隠しファイルを除外する。"""
    return not path.name.startswith("~$") and not path.name.startswith(".")


def _list_pdfs(base_dir: Path, source: Source) -> list[FileEntry]:
    if not base_dir.is_dir():
        return []
    entries: list[FileEntry] = []
    for path in base_dir.rglob("*.pdf"):
        if not path.is_file() or not _is_visible(path):
            continue
        relative = path.relative_to(base_dir).as_posix()
        updated_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
        entries.append(
            FileEntry(name=path.name, source=source, path=f"{source}/{relative}", updated_at=updated_at)
        )
    return entries


@router.get("/files", response_model=list[FileEntry])
def list_files(current_user: User = Depends(get_current_user)) -> list[FileEntry]:
    entries = _list_pdfs(Path(settings.generated_dir), "generated") + _list_pdfs(
        Path(settings.shared_dir), "shared"
    )
    entries.sort(key=lambda e: e.updated_at, reverse=True)
    return entries
