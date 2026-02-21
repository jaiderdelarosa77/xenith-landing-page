"""Puertos (interfaces) del dominio `tasks` para desacoplar infraestructura."""

from typing import Protocol

from app.domain.tasks.entities import TaskFilters
from app.domain.tasks.read_models import TaskUpdatePayload, TaskView


class TasksRepository(Protocol):
    def list_tasks(self, filters: TaskFilters) -> list[TaskView]: ...

    def get_task(self, task_id: str) -> TaskView: ...

    def update_task(self, task_id: str, payload: TaskUpdatePayload) -> TaskView: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
