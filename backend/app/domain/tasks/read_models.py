"""Modelos tipados de lectura para `tasks` (salidas/consultas)."""

from typing import TypedDict


class TaskUpdatePayload(TypedDict, total=False):
    status: str
    completed: bool


class TaskView(TypedDict, total=False):
    id: str
    title: str
    description: str | None
    status: str
    priority: str
    assignedTo: str | None
    completed: bool
