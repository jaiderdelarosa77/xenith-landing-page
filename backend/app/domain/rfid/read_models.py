"""Modelos tipados de lectura para `rfid` (salidas/consultas)."""

from typing import TypedDict


class RfidTagPayload(TypedDict, total=False):
    epc: str
    tid: str | None
    status: str
    inventoryItemId: str | None


class RfidTagView(TypedDict, total=False):
    id: str
    epc: str
    tid: str | None
    status: str
    inventoryItemId: str | None


class RfidDetectionPageView(TypedDict):
    detections: list[dict]
    total: int
    limit: int
    offset: int


class RfidMutationResult(TypedDict):
    success: bool


class RfidReadResult(TypedDict, total=False):
    success: bool
    processed: int


class RfidReadPayload(TypedDict, total=False):
    readerId: str
    timestamp: str
    detections: list[dict]
