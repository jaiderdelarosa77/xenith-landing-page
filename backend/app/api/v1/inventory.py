"""Endpoints HTTP para `inventory`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_module_edit, require_module_view
from app.composition.inventory import (
    AlreadyCheckedInError,
    AlreadyCheckedOutError,
    ContainerHasItemsError,
    DuplicateAssetTagError,
    DuplicateSerialError,
    InvalidDateFormatError,
    InvalidInventoryFiltersError,
    InvalidInventoryPayloadError,
    InventoryItemNotFoundError,
    InventoryPersistenceError,
    LostItemCheckOutError,
    ProductNotFoundOrInactiveError,
    check_in,
    check_out,
    create_item,
    delete_item,
    get_item,
    list_items,
    list_movements,
    summary,
    update_item,
)
from app.core.exceptions import bad_request, not_found
from app.db.session import get_db
from app.domain.inventory.entities import CheckInOutInput, InventoryItemInput, InventoryListFilters, MovementListFilters
from app.domain.access_control.ports import AccessUser
from app.schemas.inventory import CheckInOutRequest, InventoryItemCreateUpdateRequest

router = APIRouter(prefix='/inventory', tags=['inventory'])


def _parse_item_payload(payload: dict) -> InventoryItemInput:
    return InventoryItemInput(
        product_id=payload['productId'],
        serial_number=payload.get('serialNumber'),
        asset_tag=payload.get('assetTag'),
        item_type=payload['type'],
        status=payload['status'],
        condition=payload.get('condition'),
        location=payload.get('location'),
        container_id=payload.get('containerId'),
        purchase_date=payload.get('purchaseDate'),
        purchase_price=payload.get('purchasePrice'),
        warranty_expiry=payload.get('warrantyExpiry'),
        notes=payload.get('notes'),
    )


def _parse_check_in_out(payload: dict) -> CheckInOutInput:
    return CheckInOutInput(
        location=payload.get('location'),
        reason=payload.get('reason'),
        reference=payload.get('reference'),
    )


@router.get('')
def list_inventory_items(
    search: str = '',
    status_filter: str = Query('', alias='status'),
    type_filter: str = Query('', alias='type'),
    product_id: str = Query('', alias='productId'),
    container_id: str = Query('', alias='containerId'),
    _: AccessUser = Depends(require_module_view('items')),
    db: Session = Depends(get_db),
):
    try:
        return list_items(
            db,
            filters=InventoryListFilters(
                search=search,
                status_filter=status_filter,
                type_filter=type_filter,
                product_id=product_id,
                container_id=container_id,
            ),
        )
    except InvalidInventoryFiltersError as exc:
        raise bad_request(str(exc))


@router.post('', status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    payload: InventoryItemCreateUpdateRequest,
    current_user: AccessUser = Depends(require_module_edit('items')),
    db: Session = Depends(get_db),
):
    try:
        return create_item(db, payload=_parse_item_payload(payload.model_dump()), user_id=current_user.id)
    except ProductNotFoundOrInactiveError as exc:
        raise not_found(str(exc))
    except InvalidDateFormatError as exc:
        raise bad_request(str(exc))
    except InvalidInventoryPayloadError as exc:
        raise bad_request(str(exc))
    except DuplicateSerialError as exc:
        raise bad_request(str(exc))
    except DuplicateAssetTagError as exc:
        raise bad_request(str(exc))
    except InventoryPersistenceError as exc:
        raise bad_request(str(exc))


@router.get('/summary')
def inventory_summary(
    _: AccessUser = Depends(require_module_view('inventario')),
    db: Session = Depends(get_db),
):
    return summary(db)


@router.get('/movements')
def list_movements_route(
    type_filter: str = Query('', alias='type'),
    inventory_item_id: str = Query('', alias='inventoryItemId'),
    limit: int = 50,
    offset: int = 0,
    _: AccessUser = Depends(require_module_view('movimientos')),
    db: Session = Depends(get_db),
):
    try:
        return list_movements(
            db,
            filters=MovementListFilters(
                type_filter=type_filter,
                inventory_item_id=inventory_item_id,
                limit=limit,
                offset=offset,
            ),
        )
    except InvalidInventoryFiltersError as exc:
        raise bad_request(str(exc))


@router.get('/{item_id}')
def get_inventory_item(
    item_id: str,
    _: AccessUser = Depends(require_module_view('items')),
    db: Session = Depends(get_db),
):
    try:
        return get_item(db, item_id)
    except InvalidInventoryFiltersError as exc:
        raise bad_request(str(exc))
    except InventoryItemNotFoundError as exc:
        raise not_found(str(exc))


@router.put('/{item_id}')
def update_inventory_item(
    item_id: str,
    payload: InventoryItemCreateUpdateRequest,
    current_user: AccessUser = Depends(require_module_edit('items')),
    db: Session = Depends(get_db),
):
    try:
        return update_item(db, item_id=item_id, payload=_parse_item_payload(payload.model_dump()), user_id=current_user.id)
    except InventoryItemNotFoundError as exc:
        raise not_found(str(exc))
    except InvalidInventoryFiltersError as exc:
        raise bad_request(str(exc))
    except InvalidInventoryPayloadError as exc:
        raise bad_request(str(exc))
    except InvalidDateFormatError as exc:
        raise bad_request(str(exc))
    except DuplicateSerialError as exc:
        raise bad_request(str(exc))
    except DuplicateAssetTagError as exc:
        raise bad_request(str(exc))
    except InventoryPersistenceError as exc:
        raise bad_request(str(exc))


@router.delete('/{item_id}')
def delete_inventory_item(
    item_id: str,
    _: AccessUser = Depends(require_module_edit('items')),
    db: Session = Depends(get_db),
):
    try:
        return delete_item(db, item_id)
    except InvalidInventoryFiltersError as exc:
        raise bad_request(str(exc))
    except InvalidInventoryPayloadError as exc:
        raise bad_request(str(exc))
    except InventoryItemNotFoundError as exc:
        raise not_found(str(exc))
    except ContainerHasItemsError as exc:
        raise bad_request(str(exc))


@router.post('/{item_id}/check-in')
def check_in_route(
    item_id: str,
    payload: CheckInOutRequest,
    current_user: AccessUser = Depends(require_module_edit('items')),
    db: Session = Depends(get_db),
):
    try:
        return check_in(db, item_id=item_id, payload=_parse_check_in_out(payload.model_dump()), user_id=current_user.id)
    except InvalidInventoryFiltersError as exc:
        raise bad_request(str(exc))
    except InvalidInventoryPayloadError as exc:
        raise bad_request(str(exc))
    except InventoryItemNotFoundError as exc:
        raise not_found(str(exc))
    except AlreadyCheckedInError as exc:
        raise bad_request(str(exc))


@router.post('/{item_id}/check-out')
def check_out_route(
    item_id: str,
    payload: CheckInOutRequest,
    current_user: AccessUser = Depends(require_module_edit('items')),
    db: Session = Depends(get_db),
):
    try:
        return check_out(db, item_id=item_id, payload=_parse_check_in_out(payload.model_dump()), user_id=current_user.id)
    except InvalidInventoryFiltersError as exc:
        raise bad_request(str(exc))
    except InvalidInventoryPayloadError as exc:
        raise bad_request(str(exc))
    except InventoryItemNotFoundError as exc:
        raise not_found(str(exc))
    except AlreadyCheckedOutError as exc:
        raise bad_request(str(exc))
    except LostItemCheckOutError as exc:
        raise bad_request(str(exc))
