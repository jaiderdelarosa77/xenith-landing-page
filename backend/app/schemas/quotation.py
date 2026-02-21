"""Schemas Pydantic para requests/responses de `quotation`."""

from pydantic import BaseModel, Field


class QuotationItemRequest(BaseModel):
    inventoryItemId: str | None = None
    description: str = Field(min_length=3)
    quantity: int = Field(ge=1)
    unitPrice: float = Field(ge=0)


class QuotationGroupRequest(BaseModel):
    groupId: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str | None = None
    unitPrice: float = Field(ge=0)
    quantity: int = Field(ge=1)


class QuotationCreateUpdateRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str | None = None
    clientId: str = Field(min_length=1)
    projectId: str | None = None
    status: str
    validUntil: str = Field(min_length=1)
    discount: str | None = None
    tax: str | None = None
    notes: str | None = None
    terms: str | None = None
    items: list[QuotationItemRequest] = Field(default_factory=list)
    groups: list[QuotationGroupRequest] = Field(default_factory=list)
