"""Casos de uso de `quotations`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.quotations.entities import QuotationFilters
from app.domain.quotations.ports import QuotationsRepository, UnitOfWork
from app.domain.quotations.read_models import QuotationMutationResult, QuotationPayload, QuotationView


class QuotationsUseCases:
    def __init__(self, repo: QuotationsRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def list_quotations(self, filters: QuotationFilters) -> list[QuotationView]:
        return self._repo.list_quotations(filters)

    def create_quotation(self, payload: QuotationPayload, current_user_id: str) -> QuotationView:
        try:
            result = self._repo.create_quotation(payload, current_user_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def get_quotation(self, quotation_id: str, include_deep: bool) -> QuotationView:
        return self._repo.get_quotation(quotation_id, include_deep)

    def update_quotation(self, quotation_id: str, payload: QuotationPayload) -> QuotationView:
        try:
            result = self._repo.update_quotation(quotation_id, payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def delete_quotation(self, quotation_id: str) -> QuotationMutationResult:
        try:
            result = self._repo.delete_quotation(quotation_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise
