"""Adaptador de infraestructura para `comunicados` (persistencia concreta)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class SqlAlchemyRecipientsRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_active_emails(self, user_ids: list[str]) -> list[str]:
        users = self._db.scalars(
            select(User).where(
                User.id.in_(user_ids),
                User.is_active.is_(True),
            )
        ).all()
        return [user.email for user in users]
