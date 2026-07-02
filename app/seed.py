from app.db import db_session
from app.security import hash_password

DEMO_USERS = [
    {"email": "viewer@example.com", "password": "demo-viewer", "role": "viewer"},
    {"email": "editor@example.com", "password": "demo-editor", "role": "editor"},
]


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
