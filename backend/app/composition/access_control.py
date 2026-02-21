"""Composition root de `access_control`: conecta casos de uso con adaptadores concretos."""

from sqlalchemy.orm import Session

from app.application.access_control.use_cases import AccessControlUseCases
from app.core.config import settings
from app.domain.access_control.errors import ForbiddenError, InvalidTokenError, NotAuthenticatedError, UserInactiveOrMissingError
from app.domain.access_control.ports import AccessUser
from app.infrastructure.access_control.security_tokens import SecurityTokenDecoder
from app.infrastructure.access_control.sqlalchemy_repository import SqlAlchemyAccessRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _use_cases(db: Session) -> AccessControlUseCases:
    return AccessControlUseCases(
        repo=SqlAlchemyAccessRepository(db),
        tokens=SecurityTokenDecoder(),
        uow=SqlAlchemyUnitOfWork(db),
        superadmin_email=settings.superadmin_email,
    )


def get_current_user(db: Session, token: str | None) -> AccessUser:
    return _use_cases(db).get_current_user(token)


def require_admin(db: Session, current_user: AccessUser) -> AccessUser:
    return _use_cases(db).require_admin(current_user)


def require_module_view(db: Session, current_user: AccessUser, module: str) -> AccessUser:
    return _use_cases(db).require_module_view(current_user, module)


def require_module_edit(db: Session, current_user: AccessUser, module: str) -> AccessUser:
    return _use_cases(db).require_module_edit(current_user, module)


__all__ = [
    'AccessUser',
    'ForbiddenError',
    'InvalidTokenError',
    'NotAuthenticatedError',
    'UserInactiveOrMissingError',
    'get_current_user',
    'require_admin',
    'require_module_view',
    'require_module_edit',
]
