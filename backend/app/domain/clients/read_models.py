"""Modelos tipados de lectura para `clients` (salidas/consultas)."""

from typing import TypedDict


class ClientPayload(TypedDict, total=False):
    name: str
    company: str | None
    email: str | None
    phone: str | None
    address: str | None
    notes: str | None


class ClientView(TypedDict, total=False):
    id: str
    name: str
    company: str | None
    email: str | None
    phone: str | None
    address: str | None
    notes: str | None


class ClientMutationResult(TypedDict):
    success: bool
