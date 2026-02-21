"""Puertos (contratos) del módulo de usuarios.

En hexagonal, los casos de uso dependen de estas interfaces y NO de
implementaciones concretas. Infraestructura luego implementa estos contratos.
"""

from typing import Protocol

from app.domain.users.entities import PermissionInput, UserData, UserSelectData
from app.domain.users.read_models import AuditMetadata, UserUpdatePayload


class UsersRepository(Protocol):
    """Contrato del repositorio de usuarios (persistencia)."""

    def list_for_select(self) -> list[UserSelectData]: ...

    def list_all(self) -> list[UserData]: ...

    def find_by_id(self, user_id: str) -> UserData | None: ...

    def exists_by_email(self, email: str, exclude_user_id: str | None = None) -> bool: ...

    def create_user(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: str,
        position: str | None,
        is_active: bool,
        permissions: list[PermissionInput],
    ) -> str: ...

    def update_user(self, user_id: str, updates: UserUpdatePayload) -> None: ...

    def replace_permissions(self, user_id: str, permissions: list[PermissionInput]) -> None: ...

    def deactivate_user(self, user_id: str) -> None: ...


class UsersAuditWriter(Protocol):
    """Contrato para registrar eventos de auditoría de usuarios."""

    def write(
        self,
        *,
        action: str,
        entity_id: str,
        description: str,
        metadata: AuditMetadata | None,
        performed_by: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None: ...


class PasswordHasher(Protocol):
    """Contrato para hashear contraseñas sin acoplar dominio a una librería."""

    def hash(self, password: str) -> str: ...


class UnitOfWork(Protocol):
    """Contrato transaccional: confirmar o revertir un caso de uso."""

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
