"""Puertos (interfaces) del dominio `audit` para desacoplar infraestructura."""

from typing import Protocol

from app.domain.audit.entities import AuditFilters
from app.domain.audit.read_models import AuditLogView


class AuditRepository(Protocol):
    def list_logs(self, filters: AuditFilters) -> list[AuditLogView]: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
