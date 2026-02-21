"""Adaptador de infraestructura para `profile` (persistencia concreta)."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import hash_password, verify_password
from app.models.user import User


class SqlAlchemyProfileRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_profile(self, user_id: str) -> dict:
        user = self._db.scalar(select(User).where(User.id == user_id).options(selectinload(User.permissions)))
        if not user:
            return {}
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role.value,
            'position': user.position,
            'createdAt': user.created_at,
            'permissions': [
                {
                    'module': p.module,
                    'canView': p.can_view,
                    'canEdit': p.can_edit,
                }
                for p in user.permissions
            ],
        }

    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        user = self._db.get(User, user_id)
        if not user or not user.password or not verify_password(current_password, user.password):
            return False
        user.password = hash_password(new_password)
        self._db.flush()
        return True
