"""Puertos del caso de uso de bootstrap de superadmin."""

from typing import Protocol


class SuperadminGateway(Protocol):
    """Contrato para crear/actualizar el superadmin en almacenamiento."""

    def ensure_superadmin(
        self,
        email: str,
        name: str,
        password: str | None,
        force_password_reset: bool,
    ) -> str: ...


class UnitOfWork(Protocol):
    """Contrato transaccional para confirmar/revertir bootstrap."""

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
