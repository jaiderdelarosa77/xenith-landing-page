"""Schemas Pydantic para requests/responses de `rfid`."""

from pydantic import BaseModel, Field


class RfidTagCreateUpdateRequest(BaseModel):
    epc: str = Field(min_length=1)
    tid: str | None = None
    inventoryItemId: str | None = None
    status: str = 'UNASSIGNED'


class RfidEnrollmentRequest(BaseModel):
    inventoryItemId: str = Field(min_length=1)


class RfidReadItem(BaseModel):
    epc: str = Field(min_length=1)
    tid: str | None = None
    rssi: int | None = None
    direction: str | None = None
    timestamp: str | None = None


class RfidReadRequest(BaseModel):
    readerId: str = Field(min_length=1)
    readerName: str | None = None
    reads: list[RfidReadItem]
    apiKey: str = Field(min_length=1)
