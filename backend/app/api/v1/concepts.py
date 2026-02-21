"""Endpoints HTTP para `concepts`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_module_edit, require_module_view
from app.core.exceptions import not_found
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.schemas.concept import ConceptCreateUpdateRequest
from app.composition.concepts import (
    ConceptNotFoundError,
    ConceptSupplierNotFoundError,
    create_concept,
    delete_concept,
    get_concept,
    list_concepts,
    update_concept,
)

router = APIRouter(prefix='/concepts', tags=['concepts'])


@router.get('')
def list_concepts_route(
    search: str = '',
    category: str = '',
    supplier_id: str = Query('', alias='supplierId'),
    is_active: str = Query('', alias='isActive'),
    _: AccessUser = Depends(require_module_view('conceptos')),
    db: Session = Depends(get_db),
):
    return list_concepts(
        db,
        search=search,
        category=category,
        supplier_id=supplier_id,
        is_active=is_active,
    )


@router.post('', status_code=status.HTTP_201_CREATED)
def create_concept_route(
    payload: ConceptCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('conceptos')),
    db: Session = Depends(get_db),
):
    try:
        return create_concept(db, payload=payload.model_dump())
    except ConceptSupplierNotFoundError as exc:
        raise not_found(str(exc))


@router.get('/{concept_id}')
def get_concept_route(
    concept_id: str,
    _: AccessUser = Depends(require_module_view('conceptos')),
    db: Session = Depends(get_db),
):
    try:
        return get_concept(db, concept_id)
    except ConceptNotFoundError as exc:
        raise not_found(str(exc))


@router.put('/{concept_id}')
def update_concept_route(
    concept_id: str,
    payload: ConceptCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('conceptos')),
    db: Session = Depends(get_db),
):
    try:
        return update_concept(db, concept_id=concept_id, payload=payload.model_dump())
    except ConceptNotFoundError as exc:
        raise not_found(str(exc))
    except ConceptSupplierNotFoundError as exc:
        raise not_found(str(exc))


@router.delete('/{concept_id}')
def delete_concept_route(
    concept_id: str,
    _: AccessUser = Depends(require_module_edit('conceptos')),
    db: Session = Depends(get_db),
):
    try:
        return delete_concept(db, concept_id)
    except ConceptNotFoundError as exc:
        raise not_found(str(exc))
