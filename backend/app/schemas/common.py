"""Schemas Pydantic para requests/responses de `common`."""

from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict | list | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorBody
