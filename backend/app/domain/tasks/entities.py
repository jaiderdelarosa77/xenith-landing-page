"""Entidades y estructuras de negocio del dominio `tasks`."""

from dataclasses import dataclass


@dataclass(slots=True)
class TaskFilters:
    search: str
    status_filter: str
    priority: str
    assigned_to: str
    my_tasks: bool
    current_user_id: str
