"""Puertos (interfaces) del dominio `comunicados` para desacoplar infraestructura."""

from typing import Protocol


class RecipientsRepository(Protocol):
    def list_active_emails(self, user_ids: list[str]) -> list[str]: ...


class EmailProvider(Protocol):
    def send(self, *, from_email: str, to: list[str], bcc: list[str], subject: str, body: str) -> str | None: ...


class AuditWriter(Protocol):
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
    ) -> None: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
