"""Composition root de `inventory`: conecta casos de uso con adaptadores concretos."""

from app.application.inventory.use_cases import InventoryUseCases
from app.domain.inventory.entities import CheckInOutInput, InventoryItemInput, InventoryListFilters, MovementListFilters
from app.domain.inventory.errors import (
    AlreadyCheckedInError,
    AlreadyCheckedOutError,
    ContainerHasItemsError,
    DuplicateAssetTagError,
    DuplicateSerialError,
    InvalidDateFormatError,
    InvalidInventoryFiltersError,
    InvalidInventoryPayloadError,
    InventoryItemNotFoundError,
    InventoryPersistenceError,
    LostItemCheckOutError,
    ProductNotFoundOrInactiveError,
)
from app.domain.inventory.read_models import (
    InventoryCheckInOutResult,
    InventoryItemView,
    InventoryMovementsPageView,
    InventoryMutationResult,
    InventorySummaryView,
)
from app.infrastructure.inventory.sqlalchemy_repository import SqlAlchemyInventoryRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _use_cases(db) -> InventoryUseCases:
    return InventoryUseCases(
        repo=SqlAlchemyInventoryRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )


def list_items(db, *, filters: InventoryListFilters) -> list[InventoryItemView]:
    return _use_cases(db).list_items(filters)


def create_item(db, *, payload: InventoryItemInput, user_id: str) -> InventoryItemView:
    return _use_cases(db).create_item(payload, user_id)


def summary(db) -> InventorySummaryView:
    return _use_cases(db).summary()


def list_movements(db, *, filters: MovementListFilters) -> InventoryMovementsPageView:
    return _use_cases(db).list_movements(filters)


def get_item(db, item_id: str) -> InventoryItemView:
    return _use_cases(db).get_item(item_id)


def update_item(db, *, item_id: str, payload: InventoryItemInput, user_id: str) -> InventoryItemView:
    return _use_cases(db).update_item(item_id, payload, user_id)


def delete_item(db, item_id: str) -> InventoryMutationResult:
    return _use_cases(db).delete_item(item_id)


def check_in(db, *, item_id: str, payload: CheckInOutInput, user_id: str) -> InventoryCheckInOutResult:
    return _use_cases(db).check_in(item_id, payload, user_id)


def check_out(db, *, item_id: str, payload: CheckInOutInput, user_id: str) -> InventoryCheckInOutResult:
    return _use_cases(db).check_out(item_id, payload, user_id)


__all__ = [
    'AlreadyCheckedInError',
    'AlreadyCheckedOutError',
    'ContainerHasItemsError',
    'DuplicateAssetTagError',
    'DuplicateSerialError',
    'InvalidDateFormatError',
    'InvalidInventoryFiltersError',
    'InvalidInventoryPayloadError',
    'InventoryItemNotFoundError',
    'InventoryPersistenceError',
    'LostItemCheckOutError',
    'ProductNotFoundOrInactiveError',
    'check_in',
    'check_out',
    'create_item',
    'delete_item',
    'get_item',
    'list_items',
    'list_movements',
    'summary',
    'update_item',
]
