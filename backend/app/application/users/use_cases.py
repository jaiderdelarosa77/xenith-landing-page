"""Casos de uso del módulo de usuarios.

Esta capa orquesta reglas de negocio:
- valida invariantes (ej: no duplicar email, proteger superadmin),
- coordina repositorio + auditoría + hash de password,
- controla commit/rollback de la transacción.
"""

from app.domain.users.entities import PermissionInput, RequestContext, UserData, UserSelectData
from app.domain.users.errors import (
    SuperadminProtectionError,
    SuperadminRoleAssignmentError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.domain.users.ports import PasswordHasher, UnitOfWork, UsersAuditWriter, UsersRepository
from app.domain.users.read_models import AuditMetadata, UserUpdatePayload


class UsersUseCases:
    """Servicio de aplicación para operaciones de usuarios."""

    def __init__(
        self,
        users: UsersRepository,
        audit: UsersAuditWriter,
        passwords: PasswordHasher,
        uow: UnitOfWork,
        superadmin_email: str,
    ) -> None:
        self._users = users
        self._audit = audit
        self._passwords = passwords
        self._uow = uow
        self._superadmin_email = superadmin_email

    def list_users(self, for_select: bool) -> list[UserData | UserSelectData]:
        """Lista usuarios para vista completa o selector liviano."""
        if for_select:
            return self._users.list_for_select()
        return self._users.list_all()

    def get_user(self, user_id: str) -> UserData:
        """Obtiene un usuario por ID y falla con error de dominio si no existe."""
        user = self._users.find_by_id(user_id)
        if not user:
            raise UserNotFoundError('Usuario no encontrado')
        return user

    def create_user(
        self,
        *,
        name: str,
        email: str,
        password: str,
        role: str,
        position: str | None,
        permissions: list[PermissionInput],
        ctx: RequestContext,
    ) -> UserData:
        """Crea un usuario, registra auditoría y confirma transacción."""
        normalized_email = email.lower()
        if self._users.exists_by_email(normalized_email):
            raise UserAlreadyExistsError('Ya existe un usuario con este email')

        if role == 'SUPERADMIN':
            raise SuperadminRoleAssignmentError('No se puede crear otro superadmin')

        try:
            user_id = self._users.create_user(
                name=name,
                email=normalized_email,
                password_hash=self._passwords.hash(password),
                role=role,
                position=position,
                is_active=True,
                permissions=permissions,
            )

            self._audit.write(
                action='USER_CREATED',
                entity_id=user_id,
                description=f'Usuario creado: {normalized_email}',
                metadata={'userId': user_id, 'userEmail': normalized_email, 'role': role},
                performed_by=ctx.performed_by,
                ip_address=ctx.ip_address,
                user_agent=ctx.user_agent,
            )
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise

        return self.get_user(user_id)

    def update_user(
        self,
        *,
        user_id: str,
        updates: UserUpdatePayload,
        permissions: list[PermissionInput] | None,
        ctx: RequestContext,
    ) -> UserData:
        """Actualiza datos/permisos y deja traza de auditoría."""
        user = self._users.find_by_id(user_id)
        if not user:
            raise UserNotFoundError('Usuario no encontrado')

        if user.email == self._superadmin_email:
            raise SuperadminProtectionError('No se puede modificar al superadmin')

        audit_action = 'USER_UPDATED'
        audit_description = f'Usuario actualizado: {user.email}'
        audit_metadata: AuditMetadata = {'userId': user_id, 'userEmail': user.email}

        safe_updates: UserUpdatePayload = {**updates}

        if safe_updates.get('role') == 'SUPERADMIN':
            raise SuperadminRoleAssignmentError('No se puede asignar rol de superadmin')

        if 'email' in safe_updates:
            normalized_email = safe_updates['email'].lower()
            if self._users.exists_by_email(normalized_email, exclude_user_id=user_id):
                raise UserAlreadyExistsError('Ya existe un usuario con este email')
            safe_updates['email'] = normalized_email

        if 'isActive' in safe_updates:
            safe_updates['is_active'] = safe_updates.pop('isActive')
        if 'password' in safe_updates:
            safe_updates['password'] = self._passwords.hash(safe_updates['password'])

        try:
            if permissions is not None:
                old_permissions_map = {
                    perm.module: {
                        'canView': perm.can_view,
                        'canEdit': perm.can_edit,
                    }
                    for perm in user.permissions
                }
                new_permissions_map = {
                    perm.module: {
                        'canView': perm.can_view,
                        'canEdit': perm.can_edit,
                    }
                    for perm in permissions
                }

                permission_changes: list[str] = []
                modules = sorted(set(old_permissions_map.keys()) | set(new_permissions_map.keys()))
                for module in modules:
                    old_perm = old_permissions_map.get(module)
                    new_perm = new_permissions_map.get(module)
                    if old_perm == new_perm:
                        continue

                    if old_perm is None and new_perm is not None:
                        permission_changes.append(f'{module}: agregado ({_permission_summary(new_perm["canView"], new_perm["canEdit"])})')
                        continue

                    if old_perm is not None and new_perm is None:
                        permission_changes.append(f'{module}: removido ({_permission_summary(old_perm["canView"], old_perm["canEdit"])})')
                        continue

                    if old_perm is not None and new_perm is not None:
                        permission_changes.append(
                            f'{module}: {_permission_summary(old_perm["canView"], old_perm["canEdit"])} -> {_permission_summary(new_perm["canView"], new_perm["canEdit"])}'
                        )

                if permission_changes:
                    audit_action = 'USER_PERMISSIONS_CHANGED'
                    audit_description = f'Permisos actualizados: {user.email}'
                    audit_metadata['changes'] = permission_changes

                self._users.replace_permissions(user_id, permissions)

            self._users.update_user(user_id, safe_updates)

            self._audit.write(
                action=audit_action,
                entity_id=user_id,
                description=audit_description,
                metadata=audit_metadata,
                performed_by=ctx.performed_by,
                ip_address=ctx.ip_address,
                user_agent=ctx.user_agent,
            )
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
        return self.get_user(user_id)

    def deactivate_user(self, user_id: str, ctx: RequestContext) -> None:
        """Desactiva usuario (soft delete) con auditoría."""
        user = self._users.find_by_id(user_id)
        if not user:
            raise UserNotFoundError('Usuario no encontrado')

        if user.email == self._superadmin_email:
            raise SuperadminProtectionError('No se puede eliminar al superadmin')

        try:
            self._users.deactivate_user(user_id)
            self._audit.write(
                action='USER_DEACTIVATED',
                entity_id=user_id,
                description=f'Usuario desactivado: {user.email}',
                metadata={'userId': user_id, 'userEmail': user.email},
                performed_by=ctx.performed_by,
                ip_address=ctx.ip_address,
                user_agent=ctx.user_agent,
            )
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise


def _permission_summary(can_view: bool, can_edit: bool) -> str:
    view_label = 'si' if can_view else 'no'
    edit_label = 'si' if can_edit else 'no'
    return f'ver: {view_label}, editar: {edit_label}'
