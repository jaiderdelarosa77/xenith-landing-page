"""Modelos tipados de lectura para `quotations` (salidas/consultas)."""

from typing import TypedDict


class QuotationItemPayload(TypedDict, total=False):
    inventoryItemId: str | None
    description: str
    quantity: int
    unitPrice: float


class QuotationGroupPayload(TypedDict, total=False):
    groupId: str
    name: str
    description: str | None
    unitPrice: float
    quantity: int


class QuotationPayload(TypedDict, total=False):
    title: str
    description: str | None
    clientId: str
    projectId: str | None
    status: str
    validUntil: str
    discount: float | None
    tax: float | None
    notes: str | None
    terms: str | None
    items: list[QuotationItemPayload]
    groups: list[QuotationGroupPayload]


class QuotationView(TypedDict, total=False):
    id: str
    quotationNumber: str
    title: str
    description: str | None
    clientId: str
    projectId: str | None
    createdBy: str
    status: str
    validUntil: object
    subtotal: float
    tax: float
    discount: float
    total: float
    notes: str | None
    terms: str | None
    createdAt: object
    updatedAt: object
    items: list[dict]
    groups: list[dict]


class QuotationMutationResult(TypedDict):
    success: bool
