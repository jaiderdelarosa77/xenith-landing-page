"""Puertos (interfaces) del dominio `auth` para desacoplar infraestructura."""

from datetime import datetime
from typing import Protocol

from app.domain.auth.entities import RefreshTokenRecord, UserAccount
from app.domain.auth.read_models import TokenClaims


class UserAccountRepository(Protocol):
    def find_by_email(self, email: str) -> UserAccount | None: ...

    def find_by_id(self, user_id: str) -> UserAccount | None: ...


class RefreshTokenRepository(Protocol):
    def add(self, user_id: str, token_hash: str, expires_at: datetime) -> None: ...

    def find_active_by_hash(self, token_hash: str) -> RefreshTokenRecord | None: ...

    def mark_revoked(self, token_id: str) -> None: ...


class PasswordService(Protocol):
    def verify(self, password: str, password_hash: str) -> bool: ...

    def hash(self, password: str) -> str: ...


class TokenService(Protocol):
    def create_access(self, user_id: str) -> str: ...

    def create_refresh(self, user_id: str) -> str: ...

    def decode_refresh(self, token: str) -> TokenClaims: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
