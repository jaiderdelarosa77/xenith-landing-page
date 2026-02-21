"""Puertos (interfaces) del dominio `profile` para desacoplar infraestructura."""

from typing import Protocol

from app.domain.profile.read_models import ProfileView


class ProfileRepository(Protocol):
    def get_profile(self, user_id: str) -> ProfileView: ...

    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
