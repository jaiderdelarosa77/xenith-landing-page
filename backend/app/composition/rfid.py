"""Composition root de `rfid`: conecta casos de uso con adaptadores concretos."""

from app.application.rfid.use_cases import RfidUseCases
from app.domain.rfid.entities import DetectionFilters, TagFilters
from app.domain.rfid.errors import (
    DuplicateEpcError,
    InvalidApiKeyError,
    InvalidTimestampError,
    InventoryItemAlreadyLinkedError,
    InventoryItemNotFoundError,
    TagAlreadyLinkedError,
    TagNotFoundError,
)
from app.domain.rfid.read_models import (
    RfidDetectionPageView,
    RfidMutationResult,
    RfidReadPayload,
    RfidReadResult,
    RfidTagPayload,
    RfidTagView,
)
from app.infrastructure.rfid.sqlalchemy_repository import SqlAlchemyRfidRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _use_cases(db) -> RfidUseCases:
    return RfidUseCases(
        repo=SqlAlchemyRfidRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )


def list_tags(db, *, filters: TagFilters) -> list[RfidTagView]:
    return _use_cases(db).list_tags(filters)


def create_tag(db, *, payload: RfidTagPayload) -> RfidTagView:
    return _use_cases(db).create_tag(payload)


def list_unknown_tags(db) -> list[RfidTagView]:
    return _use_cases(db).list_unknown_tags()


def get_tag(db, tag_id: str) -> RfidTagView:
    return _use_cases(db).get_tag(tag_id)


def update_tag(db, *, tag_id: str, payload: RfidTagPayload) -> RfidTagView:
    return _use_cases(db).update_tag(tag_id, payload)


def delete_tag(db, tag_id: str) -> RfidMutationResult:
    return _use_cases(db).delete_tag(tag_id)


def enroll_tag(db, *, tag_id: str, inventory_item_id: str) -> RfidMutationResult:
    return _use_cases(db).enroll_tag(tag_id, inventory_item_id)


def unenroll_tag(db, *, tag_id: str) -> RfidMutationResult:
    return _use_cases(db).unenroll_tag(tag_id)


def list_detections(db, *, filters: DetectionFilters) -> RfidDetectionPageView:
    return _use_cases(db).list_detections(filters)


def process_read(db, *, payload: RfidReadPayload, api_key: str) -> RfidReadResult:
    return _use_cases(db).process_read(payload, api_key)


__all__ = [
    'DuplicateEpcError',
    'InvalidApiKeyError',
    'InvalidTimestampError',
    'InventoryItemAlreadyLinkedError',
    'InventoryItemNotFoundError',
    'TagAlreadyLinkedError',
    'TagNotFoundError',
    'create_tag',
    'delete_tag',
    'enroll_tag',
    'get_tag',
    'list_detections',
    'list_tags',
    'list_unknown_tags',
    'process_read',
    'unenroll_tag',
    'update_tag',
]
