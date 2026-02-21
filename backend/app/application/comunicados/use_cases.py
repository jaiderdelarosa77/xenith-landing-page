"""Casos de uso de `comunicados`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.comunicados.errors import ComunicadoRecipientsNotFoundError
from app.domain.comunicados.ports import AuditWriter, EmailProvider, RecipientsRepository, UnitOfWork
from app.domain.comunicados.read_models import ComunicadoResult


class ComunicadosUseCases:
    def __init__(
        self,
        *,
        recipients: RecipientsRepository,
        provider: EmailProvider,
        audit: AuditWriter,
        uow: UnitOfWork,
        from_email: str,
    ) -> None:
        self._recipients = recipients
        self._provider = provider
        self._audit = audit
        self._uow = uow
        self._from_email = from_email

    def send_comunicado(
        self,
        *,
        subject: str,
        body: str,
        recipient_ids: list[str],
        performed_by: str,
        performer_email: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> ComunicadoResult:
        bcc_emails = self._recipients.list_active_emails(recipient_ids)
        if len(bcc_emails) == 0:
            raise ComunicadoRecipientsNotFoundError('No se encontraron destinatarios activos')

        try:
            provider_id = self._provider.send(
                from_email=self._from_email,
                to=[performer_email],
                bcc=bcc_emails,
                subject=subject,
                body=body,
            )
            self._audit.log_sent(
                provider_id=provider_id,
                subject=subject,
                recipients=len(bcc_emails),
                recipient_ids=recipient_ids,
                performed_by=performed_by,
                performer_email=performer_email,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise

        return {
            'message': f'Comunicado enviado a {len(bcc_emails)} usuario(s)',
            'id': provider_id,
        }
