"""Adaptador de infraestructura para `auth` (persistencia concreta)."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.auth.entities import RefreshTokenRecord, UserAccount
from app.models.refresh_token import RefreshToken
from app.models.user import User


class SqlAlchemyAuthRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def find_by_email(self, email: str) -> UserAccount | None:
        user = self._db.scalar(select(User).where(User.email == email))
        if not user:
            return None
        return self._to_entity(user)

    def find_by_id(self, user_id: str) -> UserAccount | None:
        user = self._db.scalar(select(User).where(User.id == user_id))
        if not user:
            return None
        return self._to_entity(user)

    @staticmethod
    def _to_entity(user: User) -> UserAccount:
        return UserAccount(
            id=user.id,
            email=user.email,
            name=user.name,
            image=user.image,
            role=user.role.value,
            password_hash=user.password,
            is_active=user.is_active,
        )


class SqlAlchemyRefreshTokenRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, user_id: str, token_hash: str, expires_at: datetime) -> None:
        self._db.add(
            RefreshToken(
                id=str(uuid4()),
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
                revoked=False,
            )
        )

    def find_active_by_hash(self, token_hash: str) -> RefreshTokenRecord | None:
        token_row = self._db.scalar(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
            )
        )
        if not token_row:
            return None
        return RefreshTokenRecord(
            id=token_row.id,
            user_id=token_row.user_id,
            token_hash=token_row.token_hash,
            expires_at=token_row.expires_at,
            revoked=token_row.revoked,
        )

    def mark_revoked(self, token_id: str) -> None:
        token_row = self._db.scalar(select(RefreshToken).where(RefreshToken.id == token_id))
        if token_row:
            token_row.revoked = True
