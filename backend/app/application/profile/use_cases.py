"""Casos de uso de `profile`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.profile.errors import InvalidCurrentPasswordError
from app.domain.profile.ports import ProfileRepository, UnitOfWork
from app.domain.profile.read_models import ProfileView


class ProfileUseCases:
    def __init__(self, repo: ProfileRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def get_profile(self, user_id: str) -> ProfileView:
        return self._repo.get_profile(user_id)

    def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        try:
            updated = self._repo.change_password(user_id, current_password, new_password)
            if not updated:
                raise InvalidCurrentPasswordError('La contrasena actual es incorrecta')
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
