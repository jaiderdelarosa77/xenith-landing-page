"""Puertos (interfaces) del dominio `quotations` para desacoplar infraestructura."""

from typing import Protocol

from app.domain.quotations.entities import QuotationFilters
from app.domain.quotations.read_models import QuotationMutationResult, QuotationPayload, QuotationView


class QuotationsRepository(Protocol):
    def list_quotations(self, filters: QuotationFilters) -> list[QuotationView]: ...

    def create_quotation(self, payload: QuotationPayload, current_user_id: str) -> QuotationView: ...

    def get_quotation(self, quotation_id: str, include_deep: bool) -> QuotationView: ...

    def update_quotation(self, quotation_id: str, payload: QuotationPayload) -> QuotationView: ...

    def delete_quotation(self, quotation_id: str) -> QuotationMutationResult: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
