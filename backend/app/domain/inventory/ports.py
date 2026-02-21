"""Puertos (interfaces) del dominio de inventario.

`InventoryUseCases` depende de estos contratos, no de implementaciones concretas.
"""

from typing import Protocol

from app.domain.inventory.entities import CheckInOutInput, InventoryItemInput, InventoryListFilters, MovementListFilters
from app.domain.inventory.read_models import (
    InventoryCheckInOutResult,
    InventoryItemView,
    InventoryMovementsPageView,
    InventoryMutationResult,
    InventorySummaryView,
)


class InventoryRepository(Protocol):
    """Contrato de persistencia/consulta para inventario."""

    def list_items(self, filters: InventoryListFilters) -> list[InventoryItemView]: ...

    def create_item(self, payload: InventoryItemInput, user_id: str) -> InventoryItemView: ...

    def summary(self) -> InventorySummaryView: ...

    def list_movements(self, filters: MovementListFilters) -> InventoryMovementsPageView: ...

    def get_item(self, item_id: str) -> InventoryItemView: ...

    def update_item(self, item_id: str, payload: InventoryItemInput, user_id: str) -> InventoryItemView: ...

    def delete_item(self, item_id: str) -> InventoryMutationResult: ...

    def check_in(self, item_id: str, payload: CheckInOutInput, user_id: str) -> InventoryCheckInOutResult: ...

    def check_out(self, item_id: str, payload: CheckInOutInput, user_id: str) -> InventoryCheckInOutResult: ...


class UnitOfWork(Protocol):
    """Contrato transaccional: confirma o revierte cambios."""

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
