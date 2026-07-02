from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.db import db_session
from app.models import User, Role
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_error

    email = payload.get("sub")
    if email is None:
        raise credentials_error

    with db_session() as conn:
        row = conn.execute(
            "SELECT id, email, role FROM users WHERE email = ?", (email,)
        ).fetchone()
    if row is None:
        raise credentials_error

    return User(id=row["id"], email=row["email"], role=row["role"])


def require_role(*roles: Role):
    def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="この操作を行う権限がありません",
            )
        return user

    return _check
