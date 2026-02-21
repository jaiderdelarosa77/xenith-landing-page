"""Puertos (interfaces) del dominio `access_control` para desacoplar infraestructura."""

from typing import Protocol

from app.domain.access_control.read_models import AccessTokenClaims


class AccessUser(Protocol):
    id: str
    email: str
    role: object
    is_active: bool


class TokenDecoder(Protocol):
    def decode_access(self, token: str) -> AccessTokenClaims: ...


class AccessRepository(Protocol):
    def find_user_by_id(self, user_id: str) -> AccessUser | None: ...

    def can_view_module(self, user_id: str, module: str) -> bool: ...

    def can_edit_module(self, user_id: str, module: str) -> bool: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
