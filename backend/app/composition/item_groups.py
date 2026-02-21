"""Composition root de `item_groups`: conecta casos de uso con adaptadores concretos."""

from app.application.item_groups.use_cases import ItemGroupsUseCases
from app.domain.item_groups.entities import ItemGroupFilters
from app.domain.item_groups.errors import (
    InventoryItemNotFoundError,
    ItemAlreadyInGroupError,
    ItemGroupNotFoundError,
    ItemNotInGroupError,
)
from app.infrastructure.item_groups.sqlalchemy_repository import SqlAlchemyItemGroupsRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _use_cases(db) -> ItemGroupsUseCases:
    return ItemGroupsUseCases(
        repo=SqlAlchemyItemGroupsRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )


def list_groups(db, *, search: str) -> list[dict]:
    return _use_cases(db).list_groups(ItemGroupFilters(search=search))


def create_group(db, *, payload: dict) -> dict:
    return _use_cases(db).create_group(payload)


def get_group(db, group_id: str) -> dict:
    return _use_cases(db).get_group(group_id)


def update_group(db, *, group_id: str, payload: dict) -> dict:
    return _use_cases(db).update_group(group_id, payload)


def delete_group(db, group_id: str) -> dict:
    return _use_cases(db).delete_group(group_id)


def add_item(db, *, group_id: str, payload: dict) -> dict:
    return _use_cases(db).add_item(group_id, payload)


def remove_item(db, *, group_id: str, item_id: str) -> dict:
    return _use_cases(db).remove_item(group_id, item_id)


__all__ = [
    'InventoryItemNotFoundError',
    'ItemAlreadyInGroupError',
    'ItemGroupNotFoundError',
    'ItemNotInGroupError',
    'add_item',
    'create_group',
    'delete_group',
    'get_group',
    'list_groups',
    'remove_item',
    'update_group',
]
