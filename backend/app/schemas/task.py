"""Schemas Pydantic para requests/responses de `task`."""

from pydantic import BaseModel


class TaskUpdateRequest(BaseModel):
    status: str | None = None
    completed: bool | None = None
