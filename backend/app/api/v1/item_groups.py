"""Endpoints HTTP para `item_groups`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_module_edit, require_module_view
from app.core.exceptions import bad_request, not_found
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.schemas.item_group import AddItemToGroupRequest, ItemGroupCreateUpdateRequest
from app.composition.item_groups import (
    InventoryItemNotFoundError,
    ItemAlreadyInGroupError,
    ItemGroupNotFoundError,
    ItemNotInGroupError,
    add_item,
    create_group,
    delete_group,
    get_group,
    list_groups,
    remove_item,
    update_group,
)

router = APIRouter(prefix='/item-groups', tags=['item-groups'])


@router.get('')
def list_groups_route(
    search: str = '',
    _: AccessUser = Depends(require_module_view('grupos')),
    db: Session = Depends(get_db),
):
    return list_groups(db, search=search)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_group_route(
    payload: ItemGroupCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('grupos')),
    db: Session = Depends(get_db),
):
    return create_group(db, payload=payload.model_dump())


@router.get('/{group_id}')
def get_group_route(
    group_id: str,
    _: AccessUser = Depends(require_module_view('grupos')),
    db: Session = Depends(get_db),
):
    try:
        return get_group(db, group_id)
    except ItemGroupNotFoundError as exc:
        raise not_found(str(exc))


@router.put('/{group_id}')
def update_group_route(
    group_id: str,
    payload: ItemGroupCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('grupos')),
    db: Session = Depends(get_db),
):
    try:
        return update_group(db, group_id=group_id, payload=payload.model_dump())
    except ItemGroupNotFoundError as exc:
        raise not_found(str(exc))


@router.delete('/{group_id}')
def delete_group_route(
    group_id: str,
    _: AccessUser = Depends(require_module_edit('grupos')),
    db: Session = Depends(get_db),
):
    try:
        return delete_group(db, group_id)
    except ItemGroupNotFoundError as exc:
        raise not_found(str(exc))


@router.post('/{group_id}/items', status_code=status.HTTP_201_CREATED)
def add_item_to_group_route(
    group_id: str,
    payload: AddItemToGroupRequest,
    _: AccessUser = Depends(require_module_edit('grupos')),
    db: Session = Depends(get_db),
):
    try:
        return add_item(db, group_id=group_id, payload=payload.model_dump())
    except ItemGroupNotFoundError as exc:
        raise not_found(str(exc))
    except InventoryItemNotFoundError as exc:
        raise not_found(str(exc))
    except ItemAlreadyInGroupError as exc:
        raise bad_request(str(exc))


@router.delete('/{group_id}/items/{item_id}')
def remove_item_from_group_route(
    group_id: str,
    item_id: str,
    _: AccessUser = Depends(require_module_edit('grupos')),
    db: Session = Depends(get_db),
):
    try:
        return remove_item(db, group_id=group_id, item_id=item_id)
    except ItemNotInGroupError as exc:
        raise not_found(str(exc))
