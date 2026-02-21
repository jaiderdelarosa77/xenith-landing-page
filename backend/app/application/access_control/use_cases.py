"""Casos de uso de `access_control`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.access_control.errors import ForbiddenError, NotAuthenticatedError, UserInactiveOrMissingError
from app.domain.access_control.ports import AccessRepository, AccessUser, TokenDecoder, UnitOfWork


class AccessControlUseCases:
    def __init__(self, repo: AccessRepository, tokens: TokenDecoder, uow: UnitOfWork, superadmin_email: str) -> None:
        self._repo = repo
        self._tokens = tokens
        self._uow = uow
        self._superadmin_email = superadmin_email

    def get_current_user(self, token: str | None):
        if not token:
            raise NotAuthenticatedError('No autenticado')

        payload = self._tokens.decode_access(token)
        user = self._repo.find_user_by_id(payload['sub'])
        if not user or not user.is_active:
            raise UserInactiveOrMissingError('Usuario inactivo o inexistente')
        return user

    def require_admin(self, user: AccessUser):
        role = getattr(user.role, 'value', user.role)
        if user.email == self._superadmin_email:
            return user
        if role not in {'ADMIN', 'SUPERADMIN'}:
            raise ForbiddenError('Acceso denegado')
        return user

    def require_module_view(self, user: AccessUser, module: str):
        if user.email == self._superadmin_email:
            return user
        if not self._repo.can_view_module(user.id, module):
            raise ForbiddenError('No tienes permiso para ver este recurso')
        return user

    def require_module_edit(self, user: AccessUser, module: str):
        if user.email == self._superadmin_email:
            return user
        if not self._repo.can_edit_module(user.id, module):
            raise ForbiddenError('No tienes permiso para editar este recurso')
        return user
