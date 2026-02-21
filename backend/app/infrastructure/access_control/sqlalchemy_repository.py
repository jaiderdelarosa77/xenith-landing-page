"""Adaptador de infraestructura para `access_control` (persistencia concreta)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserPermission


class SqlAlchemyAccessRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def find_user_by_id(self, user_id: str):
        return self._db.scalar(select(User).where(User.id == user_id))

    def can_view_module(self, user_id: str, module: str) -> bool:
        permission = self._db.scalar(select(UserPermission).where(UserPermission.user_id == user_id, UserPermission.module == module))
        return bool(permission and permission.can_view)

    def can_edit_module(self, user_id: str, module: str) -> bool:
        permission = self._db.scalar(select(UserPermission).where(UserPermission.user_id == user_id, UserPermission.module == module))
        return bool(permission and permission.can_edit)
