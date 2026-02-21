"""Composition root de `audit_read`: conecta casos de uso con adaptadores concretos."""

from app.application.audit.use_cases import AuditUseCases
from app.domain.audit.entities import AuditFilters
from app.infrastructure.audit.sqlalchemy_repository import SqlAlchemyAuditRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def list_logs(db, *, search: str, action: str, limit: int) -> list[dict]:
    use_cases = AuditUseCases(
        repo=SqlAlchemyAuditRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )
    return use_cases.list_logs(AuditFilters(search=search, action=action, limit=limit))
