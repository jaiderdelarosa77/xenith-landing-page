"""Modelos tipados de lectura para `concepts` (salidas/consultas)."""

from typing import TypedDict


class ConceptPayload(TypedDict, total=False):
    name: str
    category: str
    supplierId: str | None
    unit: str | None
    baseCost: float | None
    margin: float | None
    finalPrice: float | None
    notes: str | None
    isActive: bool


class ConceptView(TypedDict, total=False):
    id: str
    name: str
    category: str
    supplierId: str | None
    unit: str | None
    baseCost: float | None
    margin: float | None
    finalPrice: float | None
    notes: str | None
    isActive: bool


class ConceptMutationResult(TypedDict):
    success: bool
