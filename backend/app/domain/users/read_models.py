"""Modelos tipados de lectura para `users` (salidas/consultas)."""

from typing import TypedDict


class UserUpdatePayload(TypedDict, total=False):
    name: str
    email: str
    role: str
    position: str | None
    isActive: bool
    is_active: bool
    password: str


class AuditMetadata(TypedDict, total=False):
    userId: str
    userEmail: str
    role: str
    changes: list[str]
