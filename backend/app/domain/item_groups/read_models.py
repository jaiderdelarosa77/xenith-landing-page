"""Modelos tipados de lectura para `item_groups` (salidas/consultas)."""

from typing import TypedDict


class ItemGroupPayload(TypedDict, total=False):
    name: str
    description: str | None


class ItemGroupItemPayload(TypedDict):
    itemId: str


class ItemGroupView(TypedDict, total=False):
    id: str
    name: str
    description: str | None


class ItemGroupMutationResult(TypedDict):
    success: bool
