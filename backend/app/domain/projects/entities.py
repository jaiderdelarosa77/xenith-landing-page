"""Entidades y estructuras de negocio del dominio `projects`."""

from dataclasses import dataclass


@dataclass(slots=True)
class ProjectFilters:
    search: str
    status_filter: str
    priority: str
    client_id: str
    assigned_to: str


@dataclass(slots=True)
class ProjectTaskInput:
    title: str
    description: str | None
    assigned_to: str | None
    due_date: str | None
    priority: str


@dataclass(slots=True)
class ProjectInput:
    title: str
    description: str
    client_id: str
    assigned_to: str
    status: str
    priority: str
    start_date: str | None
    end_date: str | None
    budget: str | None
    tags: list[str] | None
    notes: str | None
    tasks: list[ProjectTaskInput]
