"""Endpoints HTTP para `users`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.exceptions import bad_request, not_found
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.schemas.user import CreateUserRequest, UpdateUserRequest, UserOut, UserSelectOut
from app.composition.users import (
    RequestContext,
    SuperadminProtectionError,
    SuperadminRoleAssignmentError,
    UserAlreadyExistsError,
    UserNotFoundError,
    create_user,
    deactivate_user,
    get_user,
    list_users,
    update_user,
)

router = APIRouter(prefix='/users', tags=['users'])


def _request_context(request: Request, performed_by: str) -> RequestContext:
    return RequestContext(
        performed_by=performed_by,
        ip_address=request.headers.get('x-forwarded-for', request.client.host if request.client else None),
        user_agent=request.headers.get('user-agent'),
    )


@router.get('', response_model=list[UserOut | UserSelectOut])
def list_users_route(
    _: AccessUser = Depends(require_admin),
    for_select: bool = Query(False, alias='forSelect'),
    db: Session = Depends(get_db),
):
    return list_users(db, for_select)


@router.post('', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_route(
    payload: CreateUserRequest,
    request: Request,
    admin: AccessUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return create_user(
            db,
            name=payload.name,
            email=payload.email,
            password=payload.password,
            role=payload.role,
            position=payload.position,
            permissions=[perm.model_dump() for perm in payload.permissions],
            ctx=_request_context(request, admin.id),
        )
    except UserAlreadyExistsError as exc:
        raise bad_request(str(exc))
    except SuperadminRoleAssignmentError as exc:
        raise bad_request(str(exc))


@router.get('/{user_id}', response_model=UserOut)
def get_user_route(user_id: str, _: AccessUser = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        return get_user(db, user_id)
    except UserNotFoundError as exc:
        raise not_found(str(exc))


@router.put('/{user_id}', response_model=UserOut)
def update_user_route(
    user_id: str,
    payload: UpdateUserRequest,
    request: Request,
    admin: AccessUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        update_data = payload.model_dump(exclude_unset=True)
        permissions = None
        if 'permissions' in update_data:
            permissions = [perm.model_dump() for perm in (payload.permissions or [])]

        return update_user(
            db,
            user_id=user_id,
            updates=update_data,
            permissions=permissions,
            ctx=_request_context(request, admin.id),
        )
    except UserNotFoundError as exc:
        raise not_found(str(exc))
    except UserAlreadyExistsError as exc:
        raise bad_request(str(exc))
    except SuperadminProtectionError as exc:
        raise bad_request(str(exc))
    except SuperadminRoleAssignmentError as exc:
        raise bad_request(str(exc))


@router.delete('/{user_id}')
def deactivate_user_route(
    user_id: str,
    request: Request,
    admin: AccessUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        deactivate_user(
            db,
            user_id=user_id,
            ctx=_request_context(request, admin.id),
        )
        return {'message': 'Usuario desactivado exitosamente'}
    except UserNotFoundError as exc:
        raise not_found(str(exc))
    except SuperadminProtectionError as exc:
        raise bad_request(str(exc))
