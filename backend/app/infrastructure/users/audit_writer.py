"""Escritor concreto de infraestructura para `users`."""

from uuid import uuid4

from sqlalchemy.orm import Session

from app.domain.users.read_models import AuditMetadata
from app.models.audit_log import AuditLog


class SqlAlchemyUsersAuditWriter:
    def __init__(self, db: Session) -> None:
        self._db = db

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
    ) -> None:
        self._db.add(
            AuditLog(
                id=str(uuid4()),
                module='usuarios',
                action=action,
                entity_type='user',
                entity_id=entity_id,
                description=description,
                metadata_json=metadata,
                performed_by=performed_by,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
