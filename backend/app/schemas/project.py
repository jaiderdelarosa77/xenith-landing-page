"""Schemas Pydantic para requests/responses de `project`."""

from pydantic import BaseModel, Field


class TaskInput(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    assignedTo: str | None = None
    dueDate: str | None = None
    priority: str


class ProjectCreateUpdateRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=10)
    clientId: str = Field(min_length=1)
    assignedTo: str = Field(min_length=1)
    status: str
    priority: str
    startDate: str | None = None
    endDate: str | None = None
    budget: str | None = None
    tags: list[str] | None = None
    notes: str | None = None
    tasks: list[TaskInput] | None = None
    notifyUsers: bool | None = None
