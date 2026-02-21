"""Puertos (interfaces) del dominio `item_groups` para desacoplar infraestructura."""

from typing import Protocol

from app.domain.item_groups.entities import ItemGroupFilters
from app.domain.item_groups.read_models import (
    ItemGroupItemPayload,
    ItemGroupMutationResult,
    ItemGroupPayload,
    ItemGroupView,
)


class ItemGroupsRepository(Protocol):
    def list_groups(self, filters: ItemGroupFilters) -> list[ItemGroupView]: ...

    def create_group(self, payload: ItemGroupPayload) -> ItemGroupView: ...

    def get_group(self, group_id: str) -> ItemGroupView: ...

    def update_group(self, group_id: str, payload: ItemGroupPayload) -> ItemGroupView: ...

    def delete_group(self, group_id: str) -> ItemGroupMutationResult: ...

    def add_item(self, group_id: str, payload: ItemGroupItemPayload) -> ItemGroupMutationResult: ...

    def remove_item(self, group_id: str, item_id: str) -> ItemGroupMutationResult: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
