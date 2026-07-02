from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.db import db_session
from app.deps import get_current_user
from app.models import LoginRequest, Token, User
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest) -> Token:
    with db_session() as conn:
        row = conn.execute(
            "SELECT email, hashed_password, role FROM users WHERE email = ?",
            (credentials.email,),
        ).fetchone()

    if row is None or not verify_password(credentials.password, row["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
        )

    token = create_access_token(subject=row["email"], role=row["role"])
    return Token(access_token=token)


@router.get("/me", response_model=User)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/config")
def auth_config() -> dict:
    return {"demo_mode": settings.demo_mode}
