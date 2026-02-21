"""Caso de uso de bootstrap para asegurar un superadmin inicial.

Se ejecuta al arrancar la app y delega persistencia al puerto `SuperadminGateway`.
"""

import logging

from app.domain.bootstrap.ports import SuperadminGateway, UnitOfWork

logger = logging.getLogger(__name__)


def ensure_superadmin_use_case(
    gateway: SuperadminGateway,
    uow: UnitOfWork,
    email: str,
    name: str,
    password: str | None,
    force_password_reset: bool,
) -> None:
    """Sincroniza el superadmin y controla commit/rollback."""
    normalized_email = email.strip().lower()
    if not normalized_email:
        logger.warning('SUPERADMIN_EMAIL no esta configurado; se omite bootstrap de superadmin')
        return

    try:
        result = gateway.ensure_superadmin(
            email=normalized_email,
            name=name,
            password=password,
            force_password_reset=force_password_reset,
        )
        if result in {'created', 'updated'}:
            uow.commit()
    except Exception:
        uow.rollback()
        raise

    if result in {'created', 'updated'}:
        logger.info('Estado de superadmin sincronizado: %s', normalized_email)
        return

    if result == 'missing_password':
        logger.warning('SUPERADMIN_PASSWORD no esta configurado; no se puede crear el superadmin %s', normalized_email)
