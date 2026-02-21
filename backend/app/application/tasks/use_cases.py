"""Casos de uso de `tasks`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.tasks.entities import TaskFilters
from app.domain.tasks.errors import NoTaskChangesError
from app.domain.tasks.ports import TasksRepository, UnitOfWork
from app.domain.tasks.read_models import TaskUpdatePayload, TaskView


class TasksUseCases:
    def __init__(self, repo: TasksRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def list_tasks(self, filters: TaskFilters) -> list[TaskView]:
        return self._repo.list_tasks(filters)

    def get_task(self, task_id: str) -> TaskView:
        return self._repo.get_task(task_id)

    def update_task(self, task_id: str, payload: TaskUpdatePayload) -> TaskView:
        if payload.get('status') is None and payload.get('completed') is None:
            raise NoTaskChangesError('No hay cambios para aplicar')
        try:
            result = self._repo.update_task(task_id, payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise
