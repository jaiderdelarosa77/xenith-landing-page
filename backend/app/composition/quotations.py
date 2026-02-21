"""Composition root de `quotations`: conecta casos de uso con adaptadores concretos."""

from fastapi import Response

from app.application.quotations.use_cases import QuotationsUseCases
from app.domain.quotations.entities import QuotationFilters
from app.domain.quotations.errors import (
    ClientNotFoundError,
    EmptyQuotationError,
    InvalidValidUntilError,
    ItemGroupNotFoundError,
    ProjectNotFoundError,
    QuotationNotFoundError,
)
from app.domain.quotations.read_models import QuotationMutationResult, QuotationPayload, QuotationView
from app.infrastructure.quotations.sqlalchemy_repository import SqlAlchemyQuotationsRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.quotations.pdf import generate_quotation_pdf_bytes


def _use_cases(db) -> QuotationsUseCases:
    return QuotationsUseCases(
        repo=SqlAlchemyQuotationsRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )


def list_quotations(db, *, search: str, status_filter: str, client_id: str, project_id: str) -> list[QuotationView]:
    return _use_cases(db).list_quotations(
        QuotationFilters(
            search=search,
            status_filter=status_filter,
            client_id=client_id,
            project_id=project_id,
        )
    )


def create_quotation(db, *, payload: QuotationPayload, current_user_id: str) -> QuotationView:
    return _use_cases(db).create_quotation(payload, current_user_id)


def get_quotation(db, quotation_id: str) -> QuotationView:
    return _use_cases(db).get_quotation(quotation_id, include_deep=True)


def update_quotation(db, *, quotation_id: str, payload: QuotationPayload) -> QuotationView:
    return _use_cases(db).update_quotation(quotation_id, payload)


def delete_quotation(db, quotation_id: str) -> QuotationMutationResult:
    return _use_cases(db).delete_quotation(quotation_id)


def download_quotation_pdf(db, quotation_id: str) -> Response:
    payload = _use_cases(db).get_quotation(quotation_id, include_deep=True)
    pdf_bytes = generate_quotation_pdf_bytes(payload)
    filename = f"Cotizacion-{payload.get('quotationNumber', quotation_id)}.pdf"
    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return Response(content=pdf_bytes, media_type='application/pdf', headers=headers)


__all__ = [
    'ClientNotFoundError',
    'EmptyQuotationError',
    'InvalidValidUntilError',
    'ItemGroupNotFoundError',
    'ProjectNotFoundError',
    'QuotationNotFoundError',
    'create_quotation',
    'delete_quotation',
    'download_quotation_pdf',
    'get_quotation',
    'list_quotations',
    'update_quotation',
]
