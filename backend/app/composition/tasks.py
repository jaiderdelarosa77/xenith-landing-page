"""Composition root de `tasks`: conecta casos de uso con adaptadores concretos."""

from app.application.tasks.use_cases import TasksUseCases
from app.domain.tasks.entities import TaskFilters
from app.domain.tasks.errors import NoTaskChangesError, TaskNotFoundError
from app.infrastructure.tasks.sqlalchemy_repository import SqlAlchemyTasksRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _use_cases(db) -> TasksUseCases:
    return TasksUseCases(
        repo=SqlAlchemyTasksRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )


def list_tasks(db, *, search: str, status_filter: str, priority: str, assigned_to: str, my_tasks: bool, current_user_id: str) -> list[dict]:
    return _use_cases(db).list_tasks(
        TaskFilters(
            search=search,
            status_filter=status_filter,
            priority=priority,
            assigned_to=assigned_to,
            my_tasks=my_tasks,
            current_user_id=current_user_id,
        )
    )


def get_task(db, task_id: str) -> dict:
    return _use_cases(db).get_task(task_id)


def update_task(db, *, task_id: str, payload: dict) -> dict:
    return _use_cases(db).update_task(task_id, payload)


__all__ = [
    'NoTaskChangesError',
    'TaskNotFoundError',
    'get_task',
    'list_tasks',
    'update_task',
]
