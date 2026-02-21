"""Endpoints HTTP para `projects`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_module_edit, require_module_view
from app.core.exceptions import bad_request, not_found
from app.db.session import get_db
from app.domain.projects.entities import ProjectFilters, ProjectInput, ProjectTaskInput
from app.composition.projects import (
    AssignedUserNotFoundError,
    ClientNotFoundError,
    InvalidDateFormatError,
    InvalidProjectFiltersError,
    InvalidProjectPayloadError,
    ProjectNotFoundError,
    ProjectPersistenceError,
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)
from app.domain.access_control.ports import AccessUser
from app.schemas.project import ProjectCreateUpdateRequest

router = APIRouter(prefix='/projects', tags=['projects'])


def _parse_project_payload(payload: dict) -> ProjectInput:
    return ProjectInput(
        title=payload['title'],
        description=payload['description'],
        client_id=payload['clientId'],
        assigned_to=payload['assignedTo'],
        status=payload['status'],
        priority=payload['priority'],
        start_date=payload.get('startDate'),
        end_date=payload.get('endDate'),
        budget=payload.get('budget'),
        tags=payload.get('tags'),
        notes=payload.get('notes'),
        tasks=[
            ProjectTaskInput(
                title=task['title'],
                description=task.get('description'),
                assigned_to=task.get('assignedTo'),
                due_date=task.get('dueDate'),
                priority=task['priority'],
            )
            for task in (payload.get('tasks') or [])
        ],
    )


@router.get('')
def list_projects_route(
    search: str = '',
    status_filter: str = Query('', alias='status'),
    priority: str = '',
    client_id: str = Query('', alias='clientId'),
    assigned_to: str = Query('', alias='assignedTo'),
    _: AccessUser = Depends(require_module_view('proyectos')),
    db: Session = Depends(get_db),
):
    try:
        return list_projects(
            db,
            filters=ProjectFilters(
                search=search,
                status_filter=status_filter,
                priority=priority,
                client_id=client_id,
                assigned_to=assigned_to,
            ),
        )
    except InvalidProjectFiltersError as exc:
        raise bad_request(str(exc))


@router.post('', status_code=status.HTTP_201_CREATED)
def create_project_route(
    payload: ProjectCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('proyectos')),
    db: Session = Depends(get_db),
):
    try:
        return create_project(db, payload=_parse_project_payload(payload.model_dump()))
    except ClientNotFoundError as exc:
        raise not_found(str(exc))
    except AssignedUserNotFoundError as exc:
        raise not_found(str(exc))
    except InvalidDateFormatError as exc:
        raise bad_request(str(exc))
    except InvalidProjectPayloadError as exc:
        raise bad_request(str(exc))
    except ProjectPersistenceError as exc:
        raise bad_request(str(exc))


@router.get('/{project_id}')
def get_project_route(
    project_id: str,
    _: AccessUser = Depends(require_module_view('proyectos')),
    db: Session = Depends(get_db),
):
    try:
        return get_project(db, project_id)
    except InvalidProjectPayloadError as exc:
        raise bad_request(str(exc))
    except ProjectNotFoundError as exc:
        raise not_found(str(exc))


@router.put('/{project_id}')
def update_project_route(
    project_id: str,
    payload: ProjectCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('proyectos')),
    db: Session = Depends(get_db),
):
    try:
        return update_project(db, project_id=project_id, payload=_parse_project_payload(payload.model_dump()))
    except ProjectNotFoundError as exc:
        raise not_found(str(exc))
    except InvalidProjectPayloadError as exc:
        raise bad_request(str(exc))
    except InvalidDateFormatError as exc:
        raise bad_request(str(exc))
    except ProjectPersistenceError as exc:
        raise bad_request(str(exc))


@router.delete('/{project_id}')
def delete_project_route(
    project_id: str,
    _: AccessUser = Depends(require_module_edit('proyectos')),
    db: Session = Depends(get_db),
):
    try:
        return delete_project(db, project_id)
    except InvalidProjectPayloadError as exc:
        raise bad_request(str(exc))
    except ProjectNotFoundError as exc:
        raise not_found(str(exc))
