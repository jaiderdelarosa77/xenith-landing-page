"""Escritor concreto de infraestructura para `comunicados`."""

from sqlalchemy.orm import Session

from app.infrastructure.audit.log_writer import create_audit_log


class SqlAlchemyComunicadoAuditWriter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def log_sent(
        self,
        *,
        provider_id: str | None,
        subject: str,
        recipients: int,
        recipient_ids: list[str],
        performed_by: str,
        performer_email: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        create_audit_log(
            self._db,
            module='comunicados',
            action='COMMUNICATION_SENT',
            entity_type='communication',
            entity_id=provider_id,
            description=f'Comunicado enviado por {performer_email} a {recipients} destinatarios',
            metadata={
                'subject': subject,
                'recipients': recipients,
                'recipientIds': recipient_ids,
                'providerId': provider_id,
            },
            performed_by=performed_by,
            ip_address=ip_address,
            user_agent=user_agent,
        )
