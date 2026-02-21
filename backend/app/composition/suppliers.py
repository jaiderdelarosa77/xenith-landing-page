"""Composition root de `suppliers`: conecta casos de uso con adaptadores concretos."""

from app.application.suppliers.use_cases import SuppliersUseCases
from app.domain.suppliers.entities import SupplierFilters
from app.domain.suppliers.errors import SupplierHasProductsError, SupplierNotFoundError
from app.infrastructure.suppliers.sqlalchemy_repository import SqlAlchemySuppliersRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _use_cases(db) -> SuppliersUseCases:
    return SuppliersUseCases(
        repo=SqlAlchemySuppliersRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )


def list_suppliers(db, *, search: str) -> list[dict]:
    return _use_cases(db).list_suppliers(SupplierFilters(search=search))


def create_supplier(db, *, payload: dict) -> dict:
    return _use_cases(db).create_supplier(payload)


def get_supplier(db, supplier_id: str) -> dict:
    return _use_cases(db).get_supplier(supplier_id)


def update_supplier(db, *, supplier_id: str, payload: dict) -> dict:
    return _use_cases(db).update_supplier(supplier_id, payload)


def delete_supplier(db, supplier_id: str) -> dict:
    return _use_cases(db).delete_supplier(supplier_id)


__all__ = [
    'SupplierHasProductsError',
    'SupplierNotFoundError',
    'create_supplier',
    'delete_supplier',
    'get_supplier',
    'list_suppliers',
    'update_supplier',
]
