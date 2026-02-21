"""Escritor concreto de infraestructura para `audit`."""

from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    *,
    module: str,
    action: str,
    entity_type: str,
    description: str,
    performed_by: str,
    entity_id: str | None = None,
    metadata: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    log = AuditLog(
        id=str(uuid4()),
        module=module,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        metadata_json=metadata,
        performed_by=performed_by,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(log)
