"""Schemas Pydantic para requests/responses de `product`."""

from pydantic import BaseModel, Field


class ProductCreateUpdateRequest(BaseModel):
    sku: str = Field(min_length=1)
    name: str = Field(min_length=2)
    description: str | None = None
    categoryId: str = Field(min_length=1)
    brand: str | None = None
    model: str | None = None
    status: str
    unitPrice: float | None = Field(default=None, ge=0)
    rentalPrice: float | None = Field(default=None, ge=0)
    imageUrl: str | None = None
    notes: str | None = None


class ProductSupplierRequest(BaseModel):
    supplierId: str = Field(min_length=1)
    supplierSku: str | None = None
    cost: float | None = Field(default=None, ge=0)
    isPreferred: bool = False
