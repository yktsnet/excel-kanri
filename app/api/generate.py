import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.config import settings
from app.db import db_session
from app.deps import get_current_user, require_role
from app.gotenberg import GotenbergError, convert_to_pdf
from app.indexer import index_document
from app.models import User
from packages.template_fill import FillError, MappingError, fill_template, load_mapping

router = APIRouter(prefix="/api", tags=["generate"])


class DocumentType(BaseModel):
    doc_type: str
    fields: list[str]


class GenerateRequest(BaseModel):
    doc_type: str
    fields: dict[str, str]


class GenerateResponse(BaseModel):
    id: int
    doc_type: str
    xlsx_path: str
    pdf_path: str | None


class DocumentRecord(BaseModel):
    id: int
    doc_type: str
    fields: dict[str, str]
    pdf_path: str
    created_at: str


@router.get("/documents/types", response_model=list[DocumentType])
def list_document_types(current_user: User = Depends(get_current_user)) -> list[DocumentType]:
    mapping_dir = Path(settings.mapping_dir)
    types: list[DocumentType] = []
    for path in sorted(mapping_dir.glob("*.yaml")):
        try:
            mapping = load_mapping(path)
        except MappingError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"マッピングの読み込みに失敗しました: {path.name}: {exc}",
            ) from exc
        types.append(DocumentType(doc_type=path.stem, fields=list(mapping.fields.keys())))
    return types


@router.get("/documents", response_model=list[DocumentRecord])
def list_documents(current_user: User = Depends(get_current_user)) -> list[DocumentRecord]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT id, doc_type, fields_json, pdf_path, created_at
            FROM documents
            WHERE pdf_path IS NOT NULL
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [
        DocumentRecord(
            id=row["id"],
            doc_type=row["doc_type"],
            fields=json.loads(row["fields_json"]),
            pdf_path=row["pdf_path"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


@router.post("/generate", response_model=GenerateResponse)
def generate_document(
    request: GenerateRequest,
    current_user: User = Depends(require_role("editor")),
) -> GenerateResponse:
    mapping_path = Path(settings.mapping_dir) / f"{request.doc_type}.yaml"
    if not mapping_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"書類種別が見つかりません: {request.doc_type}",
        )

    try:
        mapping = load_mapping(mapping_path)
    except MappingError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"マッピングの読み込みに失敗しました: {exc}",
        ) from exc

    created_at = datetime.now(timezone.utc).isoformat()
    with db_session() as conn:
        cursor = conn.execute(
            """
            INSERT INTO documents (doc_type, fields_json, xlsx_path, pdf_path, created_by, created_at)
            VALUES (?, ?, NULL, NULL, ?, ?)
            """,
            (
                request.doc_type,
                json.dumps(request.fields, ensure_ascii=False),
                current_user.email,
                created_at,
            ),
        )
        doc_id = cursor.lastrowid
    assert doc_id is not None

    generated_dir = Path(settings.generated_dir)
    xlsx_path = generated_dir / f"{request.doc_type}-{doc_id}.xlsx"
    try:
        fill_template(mapping, request.fields, xlsx_path)
    except FillError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    pdf_path = generated_dir / f"{request.doc_type}-{doc_id}.pdf"
    convert_error: str | None = None
    try:
        convert_to_pdf(xlsx_path, pdf_path)
    except GotenbergError as exc:
        convert_error = str(exc)

    with db_session() as conn:
        conn.execute(
            "UPDATE documents SET xlsx_path = ?, pdf_path = ? WHERE id = ?",
            (str(xlsx_path), None if convert_error else str(pdf_path), doc_id),
        )
        if not convert_error:
            index_document(conn, doc_id, request.doc_type, json.dumps(request.fields, ensure_ascii=False))

    if convert_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"PDF変換に失敗しました（xlsxは保存済み）: {convert_error}",
        )

    return GenerateResponse(
        id=doc_id,
        doc_type=request.doc_type,
        xlsx_path=str(xlsx_path),
        pdf_path=str(pdf_path),
    )
