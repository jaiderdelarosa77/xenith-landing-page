"""Schemas Pydantic para requests/responses de `comunicado`."""

from pydantic import BaseModel, Field


class ComunicadoRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=5000)
    userIds: list[str] = Field(min_length=1)
