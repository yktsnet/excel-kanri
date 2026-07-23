import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.generate import router as generate_router
from app.config import settings
from app.db import db_session, init_db
from app.security import create_access_token


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(settings, "db_path", str(tmp_path / "test.db"))
    init_db()
    with db_session() as conn:
        conn.executemany(
            "INSERT INTO users (email, hashed_password, role) VALUES (?, ?, ?)",
            [
                ("viewer@example.com", "unused", "viewer"),
                ("editor@example.com", "unused", "editor"),
            ],
        )
        conn.executemany(
            """
            INSERT INTO documents (doc_type, fields_json, xlsx_path, pdf_path, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "nyukyo",
                    json.dumps({"氏名": "山田太郎", "部屋番号": "101"}, ensure_ascii=False),
                    "generated/nyukyo-1.xlsx",
                    "generated/nyukyo-1.pdf",
                    "editor@example.com",
                    "2026-07-01T00:00:00+00:00",
                ),
                (
                    "nyukyo",
                    json.dumps({"氏名": "佐藤花子", "部屋番号": "202"}, ensure_ascii=False),
                    "generated/nyukyo-2.xlsx",
                    None,
                    "editor@example.com",
                    "2026-07-02T00:00:00+00:00",
                ),
                (
                    "taikyo",
                    json.dumps({"氏名": "鈴木一郎"}, ensure_ascii=False),
                    "generated/taikyo-3.xlsx",
                    "generated/taikyo-3.pdf",
                    "editor@example.com",
                    "2026-07-03T00:00:00+00:00",
                ),
            ],
        )

    app = FastAPI()
    app.include_router(generate_router)
    return TestClient(app)


def auth_header(email: str, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(email, role)}"}


def test_documents_requires_auth(client: TestClient) -> None:
    assert client.get("/api/documents").status_code == 401


@pytest.mark.parametrize(
    ("email", "role"),
    [("viewer@example.com", "viewer"), ("editor@example.com", "editor")],
)
def test_documents_allows_both_roles(client: TestClient, email: str, role: str) -> None:
    response = client.get("/api/documents", headers=auth_header(email, role))
    assert response.status_code == 200


def test_documents_returns_only_pdf_ready_rows_with_parsed_fields(client: TestClient) -> None:
    response = client.get("/api/documents", headers=auth_header("viewer@example.com", "viewer"))
    documents = response.json()

    assert [doc["doc_type"] for doc in documents] == ["taikyo", "nyukyo"]
    for doc in documents:
        assert set(doc) == {"id", "doc_type", "fields", "pdf_path", "created_at"}
        assert isinstance(doc["fields"], dict)
    assert documents[1]["fields"] == {"氏名": "山田太郎", "部屋番号": "101"}


def test_documents_sorted_by_created_at_desc(client: TestClient) -> None:
    response = client.get("/api/documents", headers=auth_header("viewer@example.com", "viewer"))
    created = [doc["created_at"] for doc in response.json()]
    assert created == sorted(created, reverse=True)
