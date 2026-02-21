"""Schemas Pydantic para requests/responses de `inventory`."""

from pydantic import BaseModel, Field


class InventoryItemCreateUpdateRequest(BaseModel):
    productId: str = Field(min_length=1)
    serialNumber: str | None = None
    assetTag: str | None = None
    type: str
    status: str
    condition: str | None = None
    location: str | None = None
    containerId: str | None = None
    purchaseDate: str | None = None
    purchasePrice: float | None = Field(default=None, ge=0)
    warrantyExpiry: str | None = None
    notes: str | None = None


class CheckInOutRequest(BaseModel):
    location: str | None = None
    reason: str | None = None
    reference: str | None = None
