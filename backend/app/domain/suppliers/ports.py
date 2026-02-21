"""Puertos (interfaces) del dominio `suppliers` para desacoplar infraestructura."""

from typing import Protocol

from app.domain.suppliers.entities import SupplierFilters
from app.domain.suppliers.read_models import SupplierMutationResult, SupplierPayload, SupplierView


class SuppliersRepository(Protocol):
    def list_suppliers(self, filters: SupplierFilters) -> list[SupplierView]: ...

    def create_supplier(self, payload: SupplierPayload) -> SupplierView: ...

    def get_supplier(self, supplier_id: str) -> SupplierView: ...

    def update_supplier(self, supplier_id: str, payload: SupplierPayload) -> SupplierView: ...

    def delete_supplier(self, supplier_id: str) -> SupplierMutationResult: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
