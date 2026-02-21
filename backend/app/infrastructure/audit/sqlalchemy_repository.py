"""Adaptador de infraestructura para `audit` (persistencia concreta)."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.domain.audit.entities import AuditFilters
from app.models.audit_log import AuditLog
from app.models.user import User


class SqlAlchemyAuditRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_logs(self, filters: AuditFilters) -> list[dict]:
        stmt = (
            select(AuditLog, User)
            .join(User, AuditLog.performed_by == User.id)
            .order_by(AuditLog.created_at.desc())
            .limit(filters.limit)
        )

        if filters.action:
            stmt = stmt.where(AuditLog.action == filters.action)

        if filters.search:
            search_like = f'%{filters.search.strip()}%'
            stmt = stmt.where(
                or_(
                    AuditLog.description.ilike(search_like),
                    AuditLog.module.ilike(search_like),
                    AuditLog.action.ilike(search_like),
                    User.email.ilike(search_like),
                    User.name.ilike(search_like),
                )
            )

        rows = self._db.execute(stmt).all()
        return [
            {
                'id': log.id,
                'module': log.module,
                'action': log.action,
                'description': log.description,
                'entityType': log.entity_type,
                'entityId': log.entity_id,
                'ipAddress': log.ip_address,
                'createdAt': log.created_at,
                'metadata': log.metadata_json,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                },
            }
            for log, user in rows
        ]
