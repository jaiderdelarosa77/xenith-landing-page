"""Schemas Pydantic para requests/responses de `auth`."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class AuthUser(BaseModel):
    id: str
    email: str
    name: str | None = None
    image: str | None = None
    role: str


class LoginResponse(BaseModel):
    success: bool
    user: AuthUser


class LogoutResponse(BaseModel):
    success: bool
    message: str
