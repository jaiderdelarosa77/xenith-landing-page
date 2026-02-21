"""Casos de uso de `item_groups`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.item_groups.entities import ItemGroupFilters
from app.domain.item_groups.ports import ItemGroupsRepository, UnitOfWork
from app.domain.item_groups.read_models import (
    ItemGroupItemPayload,
    ItemGroupMutationResult,
    ItemGroupPayload,
    ItemGroupView,
)


class ItemGroupsUseCases:
    def __init__(self, repo: ItemGroupsRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def list_groups(self, filters: ItemGroupFilters) -> list[ItemGroupView]:
        return self._repo.list_groups(filters)

    def create_group(self, payload: ItemGroupPayload) -> ItemGroupView:
        try:
            result = self._repo.create_group(payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def get_group(self, group_id: str) -> ItemGroupView:
        return self._repo.get_group(group_id)

    def update_group(self, group_id: str, payload: ItemGroupPayload) -> ItemGroupView:
        try:
            result = self._repo.update_group(group_id, payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def delete_group(self, group_id: str) -> ItemGroupMutationResult:
        try:
            result = self._repo.delete_group(group_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def add_item(self, group_id: str, payload: ItemGroupItemPayload) -> ItemGroupMutationResult:
        try:
            result = self._repo.add_item(group_id, payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def remove_item(self, group_id: str, item_id: str) -> ItemGroupMutationResult:
        try:
            result = self._repo.remove_item(group_id, item_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise
