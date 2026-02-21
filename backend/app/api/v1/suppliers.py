"""Endpoints HTTP para `suppliers`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_module_edit, require_module_view
from app.core.exceptions import bad_request, not_found
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.schemas.supplier import SupplierCreateUpdateRequest
from app.composition.suppliers import (
    SupplierHasProductsError,
    SupplierNotFoundError,
    create_supplier,
    delete_supplier,
    get_supplier,
    list_suppliers,
    update_supplier,
)

router = APIRouter(prefix='/suppliers', tags=['suppliers'])


@router.get('')
def list_suppliers_route(
    search: str = '',
    _: AccessUser = Depends(require_module_view('contratistas')),
    db: Session = Depends(get_db),
):
    return list_suppliers(db, search=search)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_supplier_route(
    payload: SupplierCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('contratistas')),
    db: Session = Depends(get_db),
):
    return create_supplier(db, payload=payload.model_dump())


@router.get('/{supplier_id}')
def get_supplier_route(
    supplier_id: str,
    _: AccessUser = Depends(require_module_view('contratistas')),
    db: Session = Depends(get_db),
):
    try:
        return get_supplier(db, supplier_id)
    except SupplierNotFoundError as exc:
        raise not_found(str(exc))


@router.put('/{supplier_id}')
def update_supplier_route(
    supplier_id: str,
    payload: SupplierCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('contratistas')),
    db: Session = Depends(get_db),
):
    try:
        return update_supplier(db, supplier_id=supplier_id, payload=payload.model_dump())
    except SupplierNotFoundError as exc:
        raise not_found(str(exc))


@router.delete('/{supplier_id}')
def delete_supplier_route(
    supplier_id: str,
    _: AccessUser = Depends(require_module_edit('contratistas')),
    db: Session = Depends(get_db),
):
    try:
        return delete_supplier(db, supplier_id)
    except SupplierNotFoundError as exc:
        raise not_found(str(exc))
    except SupplierHasProductsError as exc:
        raise bad_request(str(exc))
