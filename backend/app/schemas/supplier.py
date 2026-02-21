"""Schemas Pydantic para requests/responses de `supplier`."""

from pydantic import BaseModel, Field


class SupplierCreateUpdateRequest(BaseModel):
    name: str = Field(min_length=2)
    nit: str | None = None
    contactName: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    website: str | None = None
    notes: str | None = None
    rutUrl: str | None = None
