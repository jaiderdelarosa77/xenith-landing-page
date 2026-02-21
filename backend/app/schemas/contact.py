"""Schemas Pydantic para requests/responses de `contact`."""

from pydantic import BaseModel, Field


class ContactRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=100)
    phone: str | None = None
    company: str | None = Field(default=None, max_length=100)
    subject: str = Field(min_length=5, max_length=200)
    message: str = Field(min_length=10, max_length=2000)
