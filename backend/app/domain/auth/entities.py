"""Entidades y estructuras de negocio del dominio `auth`."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class UserAccount:
    id: str
    email: str
    name: str | None
    image: str | None
    role: str
    password_hash: str | None
    is_active: bool


@dataclass(slots=True)
class RefreshTokenRecord:
    id: str
    user_id: str
    token_hash: str
    expires_at: datetime
    revoked: bool
