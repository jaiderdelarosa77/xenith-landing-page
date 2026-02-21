"""Casos de uso de `rfid`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.rfid.entities import DetectionFilters, TagFilters
from app.domain.rfid.ports import RfidRepository, UnitOfWork
from app.domain.rfid.read_models import (
    RfidDetectionPageView,
    RfidMutationResult,
    RfidReadPayload,
    RfidReadResult,
    RfidTagPayload,
    RfidTagView,
)


class RfidUseCases:
    def __init__(self, repo: RfidRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def list_tags(self, filters: TagFilters) -> list[RfidTagView]:
        return self._repo.list_tags(filters)

    def create_tag(self, payload: RfidTagPayload) -> RfidTagView:
        try:
            result = self._repo.create_tag(payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def list_unknown_tags(self) -> list[RfidTagView]:
        return self._repo.list_unknown_tags()

    def get_tag(self, tag_id: str) -> RfidTagView:
        return self._repo.get_tag(tag_id)

    def update_tag(self, tag_id: str, payload: RfidTagPayload) -> RfidTagView:
        try:
            result = self._repo.update_tag(tag_id, payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def delete_tag(self, tag_id: str) -> RfidMutationResult:
        try:
            result = self._repo.delete_tag(tag_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def enroll_tag(self, tag_id: str, inventory_item_id: str) -> RfidMutationResult:
        try:
            result = self._repo.enroll_tag(tag_id, inventory_item_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def unenroll_tag(self, tag_id: str) -> RfidMutationResult:
        try:
            result = self._repo.unenroll_tag(tag_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def list_detections(self, filters: DetectionFilters) -> RfidDetectionPageView:
        return self._repo.list_detections(filters)

    def process_read(self, payload: RfidReadPayload, api_key: str) -> RfidReadResult:
        try:
            result = self._repo.process_read(payload, api_key)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise
