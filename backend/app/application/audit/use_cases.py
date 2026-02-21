"""Casos de uso de `audit`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.audit.entities import AuditFilters
from app.domain.audit.ports import AuditRepository, UnitOfWork
from app.domain.audit.read_models import AuditLogView


class AuditUseCases:
    def __init__(self, repo: AuditRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def list_logs(self, filters: AuditFilters) -> list[AuditLogView]:
        safe_limit = min(max(filters.limit, 1), 200)
        return self._repo.list_logs(AuditFilters(search=filters.search, action=filters.action, limit=safe_limit))
