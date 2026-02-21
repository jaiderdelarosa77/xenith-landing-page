"""Modelos tipados de lectura para `audit` (salidas/consultas)."""

from typing import TypedDict


class AuditLogView(TypedDict):
    id: str
    action: str
    description: str
    createdAt: object

