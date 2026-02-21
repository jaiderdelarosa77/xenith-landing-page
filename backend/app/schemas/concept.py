"""Schemas Pydantic para requests/responses de `concept`."""

from pydantic import BaseModel, Field


class ConceptCreateUpdateRequest(BaseModel):
    name: str = Field(min_length=2)
    description: str | None = None
    supplierId: str | None = None
    unitPrice: float | None = Field(default=None, ge=0)
    category: str | None = None
    notes: str | None = None
    isActive: bool = True
