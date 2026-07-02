from typing import Literal

from pydantic import BaseModel, EmailStr

Role = Literal["viewer", "editor"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class User(BaseModel):
    id: int
    email: EmailStr
    role: Role
