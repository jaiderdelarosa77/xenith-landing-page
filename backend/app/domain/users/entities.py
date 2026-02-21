"""Entidades y estructuras de negocio del dominio `users`."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class UserPermissionData:
    id: str
    module: str
    can_view: bool
    can_edit: bool


@dataclass(slots=True)
class UserData:
    id: str
    name: str | None
    email: str
    image: str | None
    role: str
    position: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    permissions: list[UserPermissionData]


@dataclass(slots=True)
class UserSelectData:
    id: str
    name: str | None
    email: str
    image: str | None


@dataclass(slots=True)
class PermissionInput:
    module: str
    can_view: bool
    can_edit: bool


@dataclass(slots=True)
class RequestContext:
    performed_by: str
    ip_address: str | None
    user_agent: str | None
