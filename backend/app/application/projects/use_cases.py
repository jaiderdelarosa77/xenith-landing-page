"""Casos de uso de `projects`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.projects.entities import ProjectFilters, ProjectInput
from app.domain.projects.errors import (
    AssignedUserNotFoundError,
    ClientNotFoundError,
    InvalidProjectFiltersError,
    InvalidProjectPayloadError,
)
from app.domain.projects.ports import ProjectsRepository, UnitOfWork
from app.domain.projects.read_models import ProjectMutationResult, ProjectView


class ProjectsUseCases:
    def __init__(self, repo: ProjectsRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def list_projects(self, filters: ProjectFilters) -> list[ProjectView]:
        if len(filters.search) > 200:
            raise InvalidProjectFiltersError('El filtro de busqueda es demasiado largo')
        return self._repo.list_projects(filters)

    def create_project(self, payload: ProjectInput) -> ProjectView:
        self._validate_payload(payload)
        self._ensure_related_entities(payload)
        try:
            result = self._repo.create_project(payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def get_project(self, project_id: str) -> ProjectView:
        if not project_id:
            raise InvalidProjectPayloadError('ID de proyecto invalido')
        return self._repo.get_project(project_id)

    def update_project(self, project_id: str, payload: ProjectInput) -> ProjectView:
        if not project_id:
            raise InvalidProjectPayloadError('ID de proyecto invalido')
        self._validate_payload(payload)
        self._ensure_related_entities(payload)
        try:
            result = self._repo.update_project(project_id, payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def delete_project(self, project_id: str) -> ProjectMutationResult:
        if not project_id:
            raise InvalidProjectPayloadError('ID de proyecto invalido')
        try:
            result = self._repo.delete_project(project_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    @staticmethod
    def _validate_payload(payload: ProjectInput) -> None:
        if not payload.title.strip():
            raise InvalidProjectPayloadError('El titulo es obligatorio')
        if not payload.description.strip():
            raise InvalidProjectPayloadError('La descripcion es obligatoria')
        if not payload.client_id:
            raise InvalidProjectPayloadError('El cliente es obligatorio')
        if not payload.assigned_to:
            raise InvalidProjectPayloadError('El responsable es obligatorio')
        if not payload.status:
            raise InvalidProjectPayloadError('El estado del proyecto es obligatorio')
        if not payload.priority:
            raise InvalidProjectPayloadError('La prioridad del proyecto es obligatoria')
        for task in payload.tasks:
            if not task.title.strip():
                raise InvalidProjectPayloadError('El titulo de la tarea es obligatorio')
            if not task.priority:
                raise InvalidProjectPayloadError('La prioridad de la tarea es obligatoria')

    def _ensure_related_entities(self, payload: ProjectInput) -> None:
        if not self._repo.client_exists(payload.client_id):
            raise ClientNotFoundError('Cliente no encontrado')
        if not self._repo.assigned_user_exists(payload.assigned_to):
            raise AssignedUserNotFoundError('Usuario asignado no encontrado')
