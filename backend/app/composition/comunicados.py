"""Composition root de `comunicados`: conecta casos de uso con adaptadores concretos."""

from app.application.comunicados.use_cases import ComunicadosUseCases
from app.core.config import settings
from app.domain.comunicados.errors import ComunicadoProviderError, ComunicadoRecipientsNotFoundError
from app.infrastructure.comunicados.audit_writer import SqlAlchemyComunicadoAuditWriter
from app.infrastructure.comunicados.recipients_repository import SqlAlchemyRecipientsRepository
from app.infrastructure.comunicados.resend_provider import ResendEmailProvider
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _use_cases(db) -> ComunicadosUseCases:
    if not settings.resend_api_key:
        raise ComunicadoProviderError('RESEND_API_KEY no esta configurado en el backend')

    return ComunicadosUseCases(
        recipients=SqlAlchemyRecipientsRepository(db),
        provider=ResendEmailProvider(api_key=settings.resend_api_key),
        audit=SqlAlchemyComunicadoAuditWriter(db),
        uow=SqlAlchemyUnitOfWork(db),
        from_email=settings.emails_from,
    )


def send_comunicado(
    db,
    *,
    subject: str,
    body: str,
    recipient_ids: list[str],
    performed_by: str,
    performer_email: str,
    ip_address: str | None,
    user_agent: str | None,
) -> dict:
    return _use_cases(db).send_comunicado(
        subject=subject,
        body=body,
        recipient_ids=recipient_ids,
        performed_by=performed_by,
        performer_email=performer_email,
        ip_address=ip_address,
        user_agent=user_agent,
    )


__all__ = [
    'ComunicadoProviderError',
    'ComunicadoRecipientsNotFoundError',
    'send_comunicado',
]
