"""Endpoints HTTP para `tasks`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_module_edit, require_module_view
from app.core.exceptions import bad_request, not_found
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.schemas.task import TaskUpdateRequest
from app.composition.tasks import NoTaskChangesError, TaskNotFoundError, get_task, list_tasks, update_task

router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get('')
def list_tasks_route(
    search: str = '',
    status_filter: str = Query('', alias='status'),
    priority: str = '',
    assigned_to: str = Query('', alias='assignedTo'),
    my_tasks: bool = Query(False, alias='myTasks'),
    current_user: AccessUser = Depends(require_module_view('tareas')),
    db: Session = Depends(get_db),
):
    return list_tasks(
        db,
        search=search,
        status_filter=status_filter,
        priority=priority,
        assigned_to=assigned_to,
        my_tasks=my_tasks,
        current_user_id=current_user.id,
    )


@router.get('/{task_id}')
def get_task_route(
    task_id: str,
    _: AccessUser = Depends(require_module_view('tareas')),
    db: Session = Depends(get_db),
):
    try:
        return get_task(db, task_id)
    except TaskNotFoundError as exc:
        raise not_found(str(exc))


@router.patch('/{task_id}')
def update_task_route(
    task_id: str,
    payload: TaskUpdateRequest,
    _: AccessUser = Depends(require_module_edit('tareas')),
    db: Session = Depends(get_db),
):
    try:
        return update_task(db, task_id=task_id, payload=payload.model_dump())
    except TaskNotFoundError as exc:
        raise not_found(str(exc))
    except NoTaskChangesError as exc:
        raise bad_request(str(exc))
