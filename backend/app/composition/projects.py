"""Composition root de `projects`: conecta casos de uso con adaptadores concretos."""

from app.application.projects.use_cases import ProjectsUseCases
from app.domain.projects.entities import ProjectFilters, ProjectInput
from app.domain.projects.errors import (
    AssignedUserNotFoundError,
    ClientNotFoundError,
    InvalidDateFormatError,
    InvalidProjectFiltersError,
    InvalidProjectPayloadError,
    ProjectNotFoundError,
    ProjectPersistenceError,
)
from app.domain.projects.read_models import ProjectMutationResult, ProjectView
from app.infrastructure.projects.sqlalchemy_repository import SqlAlchemyProjectsRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _use_cases(db) -> ProjectsUseCases:
    return ProjectsUseCases(
        repo=SqlAlchemyProjectsRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )


def list_projects(db, *, filters: ProjectFilters) -> list[ProjectView]:
    return _use_cases(db).list_projects(filters)


def create_project(db, *, payload: ProjectInput) -> ProjectView:
    return _use_cases(db).create_project(payload)


def get_project(db, project_id: str) -> ProjectView:
    return _use_cases(db).get_project(project_id)


def update_project(db, *, project_id: str, payload: ProjectInput) -> ProjectView:
    return _use_cases(db).update_project(project_id, payload)


def delete_project(db, project_id: str) -> ProjectMutationResult:
    return _use_cases(db).delete_project(project_id)


__all__ = [
    'AssignedUserNotFoundError',
    'ClientNotFoundError',
    'InvalidDateFormatError',
    'InvalidProjectFiltersError',
    'InvalidProjectPayloadError',
    'ProjectNotFoundError',
    'ProjectPersistenceError',
    'create_project',
    'delete_project',
    'get_project',
    'list_projects',
    'update_project',
]
