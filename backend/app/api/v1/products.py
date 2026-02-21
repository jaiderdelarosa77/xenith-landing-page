"""Endpoints HTTP para `products`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_module_edit, require_module_view
from app.core.exceptions import bad_request, not_found
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.schemas.product import ProductCreateUpdateRequest, ProductSupplierRequest
from app.composition.products import (
    CategoryNotFoundError,
    DuplicateSkuError,
    ProductNotFoundError,
    ProductPersistenceError,
    ProductSupplierRelationNotFoundError,
    SupplierNotFoundError,
    add_product_supplier,
    create_product,
    delete_product,
    get_product,
    list_product_suppliers,
    list_products,
    remove_product_supplier,
    update_product,
)

router = APIRouter(prefix='/products', tags=['products'])


@router.get('')
def list_products_route(
    search: str = '',
    category: str = '',
    status_filter: str = Query('', alias='status'),
    include_deleted: bool = Query(False, alias='includeDeleted'),
    _: AccessUser = Depends(require_module_view('productos')),
    db: Session = Depends(get_db),
):
    return list_products(
        db,
        search=search,
        category=category,
        status_filter=status_filter,
        include_deleted=include_deleted,
    )


@router.post('', status_code=status.HTTP_201_CREATED)
def create_product_route(
    payload: ProductCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('productos')),
    db: Session = Depends(get_db),
):
    try:
        return create_product(db, payload=payload.model_dump())
    except CategoryNotFoundError as exc:
        raise bad_request(str(exc))
    except DuplicateSkuError as exc:
        raise bad_request(str(exc))
    except ProductPersistenceError as exc:
        raise bad_request(str(exc))


@router.get('/{product_id}')
def get_product_route(
    product_id: str,
    _: AccessUser = Depends(require_module_view('productos')),
    db: Session = Depends(get_db),
):
    try:
        return get_product(db, product_id)
    except ProductNotFoundError as exc:
        raise not_found(str(exc))


@router.put('/{product_id}')
def update_product_route(
    product_id: str,
    payload: ProductCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('productos')),
    db: Session = Depends(get_db),
):
    try:
        return update_product(db, product_id=product_id, payload=payload.model_dump())
    except ProductNotFoundError as exc:
        raise not_found(str(exc))
    except CategoryNotFoundError as exc:
        raise bad_request(str(exc))
    except DuplicateSkuError as exc:
        raise bad_request(str(exc))
    except ProductPersistenceError as exc:
        raise bad_request(str(exc))


@router.delete('/{product_id}')
def delete_product_route(
    product_id: str,
    _: AccessUser = Depends(require_module_edit('productos')),
    db: Session = Depends(get_db),
):
    try:
        return delete_product(db, product_id)
    except ProductNotFoundError as exc:
        raise not_found(str(exc))


@router.get('/{product_id}/suppliers')
def list_product_suppliers_route(
    product_id: str,
    _: AccessUser = Depends(require_module_view('productos')),
    db: Session = Depends(get_db),
):
    return list_product_suppliers(db, product_id)


@router.post('/{product_id}/suppliers', status_code=status.HTTP_201_CREATED)
def add_product_supplier_route(
    product_id: str,
    payload: ProductSupplierRequest,
    _: AccessUser = Depends(require_module_edit('productos')),
    db: Session = Depends(get_db),
):
    try:
        return add_product_supplier(db, product_id=product_id, payload=payload.model_dump())
    except ProductNotFoundError as exc:
        raise not_found(str(exc))
    except SupplierNotFoundError as exc:
        raise not_found(str(exc))


@router.delete('/{product_id}/suppliers/{supplier_id}')
def remove_product_supplier_route(
    product_id: str,
    supplier_id: str,
    _: AccessUser = Depends(require_module_edit('productos')),
    db: Session = Depends(get_db),
):
    try:
        return remove_product_supplier(db, product_id=product_id, supplier_id=supplier_id)
    except ProductSupplierRelationNotFoundError as exc:
        raise not_found(str(exc))
