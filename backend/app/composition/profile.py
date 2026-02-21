"""Composition root de `profile`: conecta casos de uso con adaptadores concretos."""

from app.application.profile.use_cases import ProfileUseCases
from app.domain.profile.errors import InvalidCurrentPasswordError
from app.infrastructure.profile.sqlalchemy_repository import SqlAlchemyProfileRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _use_cases(db) -> ProfileUseCases:
    return ProfileUseCases(
        repo=SqlAlchemyProfileRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )


def get_profile(db, user_id: str) -> dict:
    return _use_cases(db).get_profile(user_id)


def change_password(db, *, user_id: str, current_password: str, new_password: str) -> None:
    _use_cases(db).change_password(user_id, current_password, new_password)


__all__ = [
    'InvalidCurrentPasswordError',
    'change_password',
    'get_profile',
]
