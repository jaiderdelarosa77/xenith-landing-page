"""Schemas Pydantic para requests/responses de `category`."""

from pydantic import BaseModel, Field


class CategoryCreateUpdateRequest(BaseModel):
    name: str = Field(min_length=2)
    description: str | None = None
    color: str | None = None
    icon: str | None = None
