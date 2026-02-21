"""Modelos ORM de SQLAlchemy para `refresh_token`."""

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column('userId', String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column('tokenHash', String, nullable=False, unique=True, index=True)
    expires_at: Mapped[DateTime] = mapped_column('expiresAt', DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
