"""Puertos (interfaces) del dominio `rfid` para desacoplar infraestructura."""

from typing import Protocol

from app.domain.rfid.entities import DetectionFilters, TagFilters
from app.domain.rfid.read_models import (
    RfidDetectionPageView,
    RfidMutationResult,
    RfidReadPayload,
    RfidReadResult,
    RfidTagPayload,
    RfidTagView,
)


class RfidRepository(Protocol):
    def list_tags(self, filters: TagFilters) -> list[RfidTagView]: ...

    def create_tag(self, payload: RfidTagPayload) -> RfidTagView: ...

    def list_unknown_tags(self) -> list[RfidTagView]: ...

    def get_tag(self, tag_id: str) -> RfidTagView: ...

    def update_tag(self, tag_id: str, payload: RfidTagPayload) -> RfidTagView: ...

    def delete_tag(self, tag_id: str) -> RfidMutationResult: ...

    def enroll_tag(self, tag_id: str, inventory_item_id: str) -> RfidMutationResult: ...

    def unenroll_tag(self, tag_id: str) -> RfidMutationResult: ...

    def list_detections(self, filters: DetectionFilters) -> RfidDetectionPageView: ...

    def process_read(self, payload: RfidReadPayload, api_key: str) -> RfidReadResult: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
