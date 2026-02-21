"""Composition root del módulo de usuarios.

Responsabilidad:
- crear implementaciones concretas (repositorio, auditoría, seguridad, UoW),
- inyectarlas en `UsersUseCases`,
- adaptar los datos de salida al formato esperado por la API.
"""

from sqlalchemy.orm import Session

from app.application.users.use_cases import UsersUseCases
from app.core.config import settings
from app.domain.users.entities import PermissionInput, RequestContext, UserData
from app.domain.users.read_models import UserUpdatePayload
from app.domain.users.errors import (
    SuperadminProtectionError,
    SuperadminRoleAssignmentError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.infrastructure.auth.security_service import SecurityAdapter
from app.infrastructure.users.audit_writer import SqlAlchemyUsersAuditWriter
from app.infrastructure.users.sqlalchemy_repository import SqlAlchemyUsersRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _build_use_cases(db: Session) -> UsersUseCases:
    """Arma el caso de uso con sus adaptadores concretos."""
    return UsersUseCases(
        users=SqlAlchemyUsersRepository(db),
        audit=SqlAlchemyUsersAuditWriter(db),
        passwords=SecurityAdapter(),
        uow=SqlAlchemyUnitOfWork(db),
        superadmin_email=settings.superadmin_email,
    )


def _serialize_user(user: UserData) -> dict:
    """Convierte entidad de dominio a DTO JSON-friendly para la API."""
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'position': user.position,
        'isActive': user.is_active,
        'createdAt': user.created_at,
        'updatedAt': user.updated_at,
        'permissions': [
            {
                'id': permission.id,
                'module': permission.module,
                'canView': permission.can_view,
                'canEdit': permission.can_edit,
            }
            for permission in user.permissions
        ],
    }


def list_users(db: Session, for_select: bool):
    """Fachada de composición para listar usuarios."""
    users = _build_use_cases(db).list_users(for_select)
    if for_select:
        return [
            {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'image': user.image,
            }
            for user in users
        ]

    return [_serialize_user(user) for user in users]


def create_user(
    db: Session,
    *,
    name: str,
    email: str,
    password: str,
    role: str,
    position: str | None,
    permissions: list[dict],
    ctx: RequestContext,
) -> dict:
    """Fachada de composición para crear usuario."""
    user = _build_use_cases(db).create_user(
        name=name,
        email=email,
        password=password,
        role=role,
        position=position,
        permissions=[
            PermissionInput(module=perm['module'], can_view=perm['canView'], can_edit=perm['canEdit'])
            for perm in permissions
        ],
        ctx=ctx,
    )
    return _serialize_user(user)


def get_user(db: Session, user_id: str) -> dict:
    """Fachada de composición para obtener usuario por id."""
    user = _build_use_cases(db).get_user(user_id)
    return _serialize_user(user)


def update_user(
    db: Session,
    *,
    user_id: str,
    updates: UserUpdatePayload,
    permissions: list[dict] | None,
    ctx: RequestContext,
) -> dict:
    """Fachada de composición para actualizar usuario."""
    parsed_permissions = None
    if permissions is not None:
        parsed_permissions = [
            PermissionInput(module=perm['module'], can_view=perm['canView'], can_edit=perm['canEdit'])
            for perm in permissions
        ]

    user = _build_use_cases(db).update_user(
        user_id=user_id,
        updates=updates,
        permissions=parsed_permissions,
        ctx=ctx,
    )
    return _serialize_user(user)


def deactivate_user(db: Session, *, user_id: str, ctx: RequestContext) -> None:
    """Fachada de composición para desactivar usuario."""
    _build_use_cases(db).deactivate_user(user_id=user_id, ctx=ctx)


__all__ = [
    'UserAlreadyExistsError',
    'UserNotFoundError',
    'SuperadminProtectionError',
    'SuperadminRoleAssignmentError',
    'RequestContext',
    'create_user',
    'deactivate_user',
    'get_user',
    'list_users',
    'update_user',
]
