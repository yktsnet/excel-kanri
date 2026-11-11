import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.auth import router as auth_router
from app.api.files import router as files_router
from app.api.generate import router as generate_router
from app.api.pdf import router as pdf_router
from app.api.search import router as search_router
from app.config import settings
from app.db import db_session, init_db
from app.indexer import index_document
from app.security import create_access_token, decode_access_token, hash_password


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(settings, "db_path", str(tmp_path / "test.db"))
    monkeypatch.setattr(settings, "generated_dir", str(tmp_path / "generated"))
    monkeypatch.setattr(settings, "shared_dir", str(tmp_path / "shared"))
    init_db()
    with db_session() as conn:
        conn.executemany(
            "INSERT INTO users (email, hashed_password, role) VALUES (?, ?, ?)",
            [
                ("viewer@example.com", hash_password("viewer-pass"), "viewer"),
                ("editor@example.com", hash_password("editor-pass"), "editor"),
            ],
        )

    app = FastAPI()
    for router in (auth_router, files_router, generate_router, pdf_router, search_router):
        app.include_router(router)
    return TestClient(app)


def auth_header(email: str, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(email, role)}"}


VIEWER = auth_header("viewer@example.com", "viewer")
EDITOR = auth_header("editor@example.com", "editor")


def test_login_issues_token_for_valid_credentials(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login", json={"email": "editor@example.com", "password": "editor-pass"}
    )

    assert response.status_code == 200
    payload = decode_access_token(response.json()["access_token"])
    assert payload is not None
    assert payload["sub"] == "editor@example.com"


@pytest.mark.parametrize(
    ("email", "password"),
    [("editor@example.com", "wrong-pass"), ("nobody@example.com", "editor-pass")],
)
def test_login_rejects_invalid_credentials_with_401(
    client: TestClient, email: str, password: str
) -> None:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 401


def test_document_types_lists_doc_types_and_field_order(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mapping_dir = tmp_path / "mapping"
    mapping_dir.mkdir()
    (mapping_dir / "b-type.yaml").write_text(
        "template: t.xlsx\nfields:\n  zeta: B3\n  alpha: B5\n", encoding="utf-8"
    )
    (mapping_dir / "a-type.yaml").write_text(
        "template: t.xlsx\nfields:\n  only: A1\n", encoding="utf-8"
    )
    monkeypatch.setattr(settings, "mapping_dir", str(mapping_dir))

    response = client.get("/api/documents/types", headers=VIEWER)

    assert response.status_code == 200
    assert response.json() == [
        {"doc_type": "a-type", "fields": ["only"]},
        {"doc_type": "b-type", "fields": ["zeta", "alpha"]},
    ]


def test_generate_rejects_viewer_with_403(client: TestClient) -> None:
    response = client.post(
        "/api/generate", json={"doc_type": "move-in", "fields": {}}, headers=VIEWER
    )
    assert response.status_code == 403


def test_generate_returns_404_for_unknown_doc_type(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mapping_dir = tmp_path / "mapping"
    mapping_dir.mkdir()
    monkeypatch.setattr(settings, "mapping_dir", str(mapping_dir))

    response = client.post(
        "/api/generate", json={"doc_type": "no-such-type", "fields": {}}, headers=EDITOR
    )
    assert response.status_code == 404


def test_search_returns_only_matching_documents_with_pdf(client: TestClient) -> None:
    rows = [
        ("move-in", {"family": "山田", "given": "太郎"}, "generated/move-in-1.pdf"),
        ("move-in", {"family": "山田", "given": "花子"}, None),
        ("move-out", {"name": "鈴木一郎"}, "generated/move-out-3.pdf"),
    ]
    with db_session() as conn:
        for doc_type, fields, pdf_path in rows:
            fields_json = json.dumps(fields, ensure_ascii=False)
            cursor = conn.execute(
                """
                INSERT INTO documents (doc_type, fields_json, xlsx_path, pdf_path, created_by, created_at)
                VALUES (?, ?, NULL, ?, 'editor@example.com', '2026-07-01T00:00:00+00:00')
                """,
                (doc_type, fields_json, pdf_path),
            )
            index_document(conn, cursor.lastrowid, doc_type, fields_json)

    response = client.get("/api/search", params={"q": "山田"}, headers=VIEWER)

    assert response.status_code == 200
    assert [r["pdf_path"] for r in response.json()] == ["generated/move-in-1.pdf"]


def _write_pdf(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"%PDF-1.4 dummy")


def test_files_lists_pdfs_under_generated_and_shared(client: TestClient, tmp_path: Path) -> None:
    _write_pdf(tmp_path / "generated" / "a.pdf")
    _write_pdf(tmp_path / "shared" / "sub" / "b.pdf")

    response = client.get("/api/files", headers=VIEWER)

    assert response.status_code == 200
    assert sorted(f["path"] for f in response.json()) == ["generated/a.pdf", "shared/sub/b.pdf"]


def test_pdf_serves_file_as_pdf(client: TestClient, tmp_path: Path) -> None:
    _write_pdf(tmp_path / "shared" / "b.pdf")

    response = client.get("/api/pdf/shared/b.pdf", headers=VIEWER)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content == b"%PDF-1.4 dummy"


def test_pdf_rejects_path_traversal_with_404(client: TestClient, tmp_path: Path) -> None:
    _write_pdf(tmp_path / "generated" / "a.pdf")
    _write_pdf(tmp_path / "secret.pdf")

    response = client.get("/api/pdf/generated/%2E%2E/secret.pdf", headers=VIEWER)

    assert response.status_code == 404
