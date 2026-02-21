"""Endpoints HTTP para `categories`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_module_edit, require_module_view
from app.core.exceptions import bad_request, not_found
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.schemas.category import CategoryCreateUpdateRequest
from app.composition.categories import (
    CategoryDuplicateNameError,
    CategoryHasProductsError,
    CategoryNotFoundError,
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)

router = APIRouter(prefix='/categories', tags=['categories'])


@router.get('')
def list_categories_route(
    search: str = '',
    _: AccessUser = Depends(require_module_view('categorias')),
    db: Session = Depends(get_db),
):
    return list_categories(db, search=search)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_category_route(
    payload: CategoryCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('categorias')),
    db: Session = Depends(get_db),
):
    try:
        return create_category(db, payload=payload.model_dump())
    except CategoryDuplicateNameError as exc:
        raise bad_request(str(exc))


@router.get('/{category_id}')
def get_category_route(
    category_id: str,
    _: AccessUser = Depends(require_module_view('categorias')),
    db: Session = Depends(get_db),
):
    try:
        return get_category(db, category_id)
    except CategoryNotFoundError as exc:
        raise not_found(str(exc))


@router.put('/{category_id}')
def update_category_route(
    category_id: str,
    payload: CategoryCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('categorias')),
    db: Session = Depends(get_db),
):
    try:
        return update_category(db, category_id=category_id, payload=payload.model_dump())
    except CategoryNotFoundError as exc:
        raise not_found(str(exc))
    except CategoryDuplicateNameError as exc:
        raise bad_request(str(exc))


@router.delete('/{category_id}')
def delete_category_route(
    category_id: str,
    _: AccessUser = Depends(require_module_edit('categorias')),
    db: Session = Depends(get_db),
):
    try:
        return delete_category(db, category_id)
    except CategoryNotFoundError as exc:
        raise not_found(str(exc))
    except CategoryHasProductsError as exc:
        raise bad_request(str(exc))
