"""Composition root para bootstrap de superadmin.

Este módulo decide qué adaptadores concretos se conectan al caso de uso.
"""

from sqlalchemy.orm import Session

from app.application.bootstrap.use_cases import ensure_superadmin_use_case
from app.core.config import settings
from app.infrastructure.bootstrap.sqlalchemy_gateway import SqlAlchemySuperadminGateway
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def ensure_superadmin(db: Session) -> None:
    """Ejecuta bootstrap con dependencias concretas de infraestructura."""
    ensure_superadmin_use_case(
        gateway=SqlAlchemySuperadminGateway(db),
        uow=SqlAlchemyUnitOfWork(db),
        email=settings.superadmin_email,
        name=settings.superadmin_name,
        password=settings.superadmin_password,
        force_password_reset=settings.superadmin_force_password_on_start,
    )
