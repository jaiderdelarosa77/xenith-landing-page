"""Modelos tipados de lectura para `categories` (salidas/consultas)."""

from typing import TypedDict


class CategoryPayload(TypedDict):
    name: str
    color: str | None


class CategoryView(TypedDict):
    id: str
    name: str
    color: str | None


class CategoryMutationResult(TypedDict):
    success: bool
