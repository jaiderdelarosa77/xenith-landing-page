"""Endpoints HTTP para `clients`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_module_edit, require_module_view
from app.core.exceptions import bad_request, not_found
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.schemas.client import ClientCreateUpdateRequest
from app.composition.clients import (
    ClientHasRelationsError,
    ClientNotFoundError,
    ClientPersistenceError,
    create_client,
    delete_client,
    get_client,
    list_clients,
    update_client,
)

router = APIRouter(prefix='/clients', tags=['clients'])


@router.get('')
def list_clients_route(
    search: str = Query(''),
    _: AccessUser = Depends(require_module_view('clientes')),
    db: Session = Depends(get_db),
):
    return list_clients(db, search=search)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_client_route(
    payload: ClientCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('clientes')),
    db: Session = Depends(get_db),
):
    try:
        return create_client(db, payload=payload.model_dump())
    except ClientPersistenceError as exc:
        raise bad_request(str(exc))


@router.get('/{client_id}')
def get_client_route(
    client_id: str,
    _: AccessUser = Depends(require_module_view('clientes')),
    db: Session = Depends(get_db),
):
    try:
        return get_client(db, client_id)
    except ClientNotFoundError as exc:
        raise not_found(str(exc))


@router.put('/{client_id}')
def update_client_route(
    client_id: str,
    payload: ClientCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('clientes')),
    db: Session = Depends(get_db),
):
    try:
        return update_client(db, client_id=client_id, payload=payload.model_dump())
    except ClientNotFoundError as exc:
        raise not_found(str(exc))
    except ClientPersistenceError as exc:
        raise bad_request(str(exc))


@router.delete('/{client_id}')
def delete_client_route(
    client_id: str,
    _: AccessUser = Depends(require_module_edit('clientes')),
    db: Session = Depends(get_db),
):
    try:
        return delete_client(db, client_id)
    except ClientNotFoundError as exc:
        raise not_found(str(exc))
    except ClientHasRelationsError as exc:
        raise bad_request(str(exc))
