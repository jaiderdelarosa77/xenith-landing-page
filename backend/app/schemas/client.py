"""Schemas Pydantic para requests/responses de `client`."""

from pydantic import BaseModel, EmailStr, Field


class ClientCreateUpdateRequest(BaseModel):
    name: str = Field(min_length=2)
    company: str | None = None
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    nit: str | None = None
    notes: str | None = None
    rutUrl: str | None = None
