"""Endpoints HTTP para `rfid`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_module_edit, require_module_view
from app.composition.rfid import (
    DuplicateEpcError,
    InvalidApiKeyError,
    InvalidTimestampError,
    InventoryItemAlreadyLinkedError,
    InventoryItemNotFoundError,
    TagAlreadyLinkedError,
    TagNotFoundError,
    create_tag,
    delete_tag,
    enroll_tag,
    get_tag,
    list_detections,
    list_tags,
    list_unknown_tags,
    process_read,
    unenroll_tag,
    update_tag,
)
from app.core.config import settings
from app.core.exceptions import bad_request, not_found, unauthorized
from app.db.session import get_db
from app.domain.rfid.entities import DetectionFilters, TagFilters
from app.domain.access_control.ports import AccessUser
from app.domain.rfid.read_models import RfidTagPayload
from app.schemas.rfid import RfidEnrollmentRequest, RfidReadRequest, RfidTagCreateUpdateRequest

router = APIRouter(prefix='/rfid', tags=['rfid'])


def _parse_tag_payload(payload: dict) -> RfidTagPayload:
    return {
        'epc': payload['epc'],
        'tid': payload.get('tid'),
        'status': payload.get('status', 'UNASSIGNED'),
        'inventoryItemId': payload.get('inventoryItemId'),
    }


def _parse_read_payload(payload: dict) -> dict:
    return {
        'readerId': payload['readerId'],
        'readerName': payload.get('readerName'),
        'reads': payload['reads'],
        'apiKey': payload['apiKey'],
    }


@router.get('/tags')
def list_tags_route(
    search: str = '',
    status_filter: str = Query('', alias='status'),
    _: AccessUser = Depends(require_module_view('rfid')),
    db: Session = Depends(get_db),
):
    return list_tags(db, filters=TagFilters(search=search, status_filter=status_filter))


@router.post('/tags')
def create_tag_route(
    payload: RfidTagCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('rfid')),
    db: Session = Depends(get_db),
):
    try:
        return create_tag(db, payload=_parse_tag_payload(payload.model_dump()))
    except DuplicateEpcError as exc:
        raise bad_request(str(exc))
    except InventoryItemNotFoundError as exc:
        raise not_found(str(exc))
    except InventoryItemAlreadyLinkedError as exc:
        raise bad_request(str(exc))


@router.get('/tags/unknown')
def list_unknown_tags_route(
    _: AccessUser = Depends(require_module_view('rfid')),
    db: Session = Depends(get_db),
):
    return list_unknown_tags(db)


@router.get('/tags/{tag_id}')
def get_tag_route(
    tag_id: str,
    _: AccessUser = Depends(require_module_view('rfid')),
    db: Session = Depends(get_db),
):
    try:
        return get_tag(db, tag_id)
    except TagNotFoundError as exc:
        raise not_found(str(exc))


@router.put('/tags/{tag_id}')
def update_tag_route(
    tag_id: str,
    payload: RfidTagCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('rfid')),
    db: Session = Depends(get_db),
):
    try:
        return update_tag(db, tag_id=tag_id, payload=_parse_tag_payload(payload.model_dump()))
    except TagNotFoundError as exc:
        raise not_found(str(exc))
    except DuplicateEpcError as exc:
        raise bad_request(str(exc))


@router.delete('/tags/{tag_id}')
def delete_tag_route(
    tag_id: str,
    _: AccessUser = Depends(require_module_edit('rfid')),
    db: Session = Depends(get_db),
):
    try:
        return delete_tag(db, tag_id)
    except TagNotFoundError as exc:
        raise not_found(str(exc))


@router.post('/tags/{tag_id}/enroll')
def enroll_tag_route(
    tag_id: str,
    payload: RfidEnrollmentRequest,
    _: AccessUser = Depends(require_module_edit('rfid')),
    db: Session = Depends(get_db),
):
    try:
        return enroll_tag(db, tag_id=tag_id, inventory_item_id=payload.inventoryItemId)
    except TagNotFoundError as exc:
        raise not_found(str(exc))
    except TagAlreadyLinkedError as exc:
        raise bad_request(str(exc))
    except InventoryItemNotFoundError as exc:
        raise not_found(str(exc))
    except InventoryItemAlreadyLinkedError as exc:
        raise bad_request(str(exc))


@router.delete('/tags/{tag_id}/enroll')
def unenroll_tag_route(
    tag_id: str,
    _: AccessUser = Depends(require_module_edit('rfid')),
    db: Session = Depends(get_db),
):
    try:
        return unenroll_tag(db, tag_id=tag_id)
    except TagNotFoundError as exc:
        raise not_found(str(exc))


@router.get('/detections')
def list_detections_route(
    rfid_tag_id: str = Query('', alias='rfidTagId'),
    reader_id: str = Query('', alias='readerId'),
    direction: str = '',
    limit: int = 100,
    offset: int = 0,
    _: AccessUser = Depends(require_module_view('rfid')),
    db: Session = Depends(get_db),
):
    return list_detections(
        db,
        filters=DetectionFilters(
            rfid_tag_id=rfid_tag_id,
            reader_id=reader_id,
            direction=direction,
            limit=limit,
            offset=offset,
        ),
    )


@router.post('/read')
def process_read_route(
    payload: RfidReadRequest,
    db: Session = Depends(get_db),
):
    try:
        return process_read(db, payload=_parse_read_payload(payload.model_dump()), api_key=settings.rfid_api_key)
    except InvalidApiKeyError as exc:
        raise unauthorized(str(exc))
    except InvalidTimestampError as exc:
        raise bad_request(str(exc))
