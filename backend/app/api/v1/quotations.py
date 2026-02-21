"""Endpoints HTTP para `quotations`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_module_edit, require_module_view
from app.core.exceptions import bad_request, not_found
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.schemas.quotation import QuotationCreateUpdateRequest
from app.composition.quotations import (
    ClientNotFoundError,
    EmptyQuotationError,
    InvalidValidUntilError,
    ItemGroupNotFoundError,
    ProjectNotFoundError,
    QuotationNotFoundError,
    create_quotation,
    delete_quotation,
    download_quotation_pdf,
    get_quotation,
    list_quotations,
    update_quotation,
)

router = APIRouter(prefix='/quotations', tags=['quotations'])


@router.get('')
def list_quotations_route(
    search: str = '',
    status_filter: str = Query('', alias='status'),
    client_id: str = Query('', alias='clientId'),
    project_id: str = Query('', alias='projectId'),
    _: AccessUser = Depends(require_module_view('cotizaciones')),
    db: Session = Depends(get_db),
):
    return list_quotations(
        db,
        search=search,
        status_filter=status_filter,
        client_id=client_id,
        project_id=project_id,
    )


@router.post('', status_code=status.HTTP_201_CREATED)
def create_quotation_route(
    payload: QuotationCreateUpdateRequest,
    current_user: AccessUser = Depends(require_module_edit('cotizaciones')),
    db: Session = Depends(get_db),
):
    try:
        return create_quotation(db, payload=payload.model_dump(), current_user_id=current_user.id)
    except EmptyQuotationError as exc:
        raise bad_request(str(exc))
    except ClientNotFoundError as exc:
        raise not_found(str(exc))
    except ProjectNotFoundError as exc:
        raise not_found(str(exc))
    except ItemGroupNotFoundError as exc:
        raise not_found(str(exc))
    except InvalidValidUntilError as exc:
        raise bad_request(str(exc))


@router.get('/{quotation_id}')
def get_quotation_route(
    quotation_id: str,
    _: AccessUser = Depends(require_module_view('cotizaciones')),
    db: Session = Depends(get_db),
):
    try:
        return get_quotation(db, quotation_id)
    except QuotationNotFoundError as exc:
        raise not_found(str(exc))


@router.put('/{quotation_id}')
def update_quotation_route(
    quotation_id: str,
    payload: QuotationCreateUpdateRequest,
    _: AccessUser = Depends(require_module_edit('cotizaciones')),
    db: Session = Depends(get_db),
):
    try:
        return update_quotation(db, quotation_id=quotation_id, payload=payload.model_dump())
    except QuotationNotFoundError as exc:
        raise not_found(str(exc))
    except EmptyQuotationError as exc:
        raise bad_request(str(exc))
    except ItemGroupNotFoundError as exc:
        raise not_found(str(exc))
    except InvalidValidUntilError as exc:
        raise bad_request(str(exc))


@router.delete('/{quotation_id}')
def delete_quotation_route(
    quotation_id: str,
    _: AccessUser = Depends(require_module_edit('cotizaciones')),
    db: Session = Depends(get_db),
):
    try:
        return delete_quotation(db, quotation_id)
    except QuotationNotFoundError as exc:
        raise not_found(str(exc))


@router.get('/{quotation_id}/pdf')
def download_quotation_pdf_route(
    quotation_id: str,
    _: AccessUser = Depends(require_module_view('cotizaciones')),
    db: Session = Depends(get_db),
):
    try:
        return download_quotation_pdf(db, quotation_id)
    except QuotationNotFoundError as exc:
        raise not_found(str(exc))
