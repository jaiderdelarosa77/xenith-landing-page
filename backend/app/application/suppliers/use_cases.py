"""Casos de uso de `suppliers`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.suppliers.entities import SupplierFilters
from app.domain.suppliers.ports import SuppliersRepository, UnitOfWork
from app.domain.suppliers.read_models import SupplierMutationResult, SupplierPayload, SupplierView


class SuppliersUseCases:
    def __init__(self, repo: SuppliersRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def list_suppliers(self, filters: SupplierFilters) -> list[SupplierView]:
        return self._repo.list_suppliers(filters)

    def create_supplier(self, payload: SupplierPayload) -> SupplierView:
        try:
            result = self._repo.create_supplier(payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def get_supplier(self, supplier_id: str) -> SupplierView:
        return self._repo.get_supplier(supplier_id)

    def update_supplier(self, supplier_id: str, payload: SupplierPayload) -> SupplierView:
        try:
            result = self._repo.update_supplier(supplier_id, payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def delete_supplier(self, supplier_id: str) -> SupplierMutationResult:
        try:
            result = self._repo.delete_supplier(supplier_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise
