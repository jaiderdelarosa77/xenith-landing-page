"""Schemas Pydantic para requests/responses de `item_group`."""

from pydantic import BaseModel, Field


class ItemGroupCreateUpdateRequest(BaseModel):
    name: str = Field(min_length=3)
    description: str | None = None


class AddItemToGroupRequest(BaseModel):
    inventoryItemId: str = Field(min_length=1)
    quantity: int = Field(default=1, ge=1)
    notes: str | None = None
