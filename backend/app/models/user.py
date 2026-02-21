"""Modelos ORM de SQLAlchemy para `user`."""

import enum
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class UserRole(str, enum.Enum):
    SUPERADMIN = 'SUPERADMIN'
    ADMIN = 'ADMIN'
    USER = 'USER'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    image: Mapped[str | None] = mapped_column(String, nullable=True)
    password: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER, nullable=False)
    position: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column('isActive', Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    permissions: Mapped[list['UserPermission']] = relationship('UserPermission', back_populates='user')


class UserPermission(Base):
    __tablename__ = 'user_permissions'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column('userId', String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    module: Mapped[str] = mapped_column(String, nullable=False)
    can_view: Mapped[bool] = mapped_column('canView', Boolean, default=False, nullable=False)
    can_edit: Mapped[bool] = mapped_column('canEdit', Boolean, default=False, nullable=False)
    created_at: Mapped[DateTime] = mapped_column('createdAt', DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column('updatedAt', DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship('User', back_populates='permissions')
