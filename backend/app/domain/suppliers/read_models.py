"""Modelos tipados de lectura para `suppliers` (salidas/consultas)."""

from typing import TypedDict


class SupplierPayload(TypedDict, total=False):
    name: str
    contactName: str | None
    email: str | None
    phone: str | None
    address: str | None
    nitRut: str | None
    notes: str | None


class SupplierView(TypedDict, total=False):
    id: str
    name: str
    contactName: str | None
    email: str | None
    phone: str | None
    address: str | None
    nitRut: str | None
    notes: str | None


class SupplierMutationResult(TypedDict):
    success: bool
