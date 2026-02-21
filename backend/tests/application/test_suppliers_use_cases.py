import pytest

from app.application.suppliers.use_cases import SuppliersUseCases
from app.domain.suppliers.entities import SupplierFilters


class FakeRepo:
    def list_suppliers(self, filters):
        return [{'id': 's1', 'filters': filters}]

    def create_supplier(self, payload: dict):
        return {'id': 's2'}

    def get_supplier(self, supplier_id: str):
        return {'id': supplier_id}

    def update_supplier(self, supplier_id: str, payload: dict):
        return {'id': supplier_id}

    def delete_supplier(self, supplier_id: str):
        return {'success': True}


class FailingRepo(FakeRepo):
    def delete_supplier(self, supplier_id: str):
        raise RuntimeError('db error')


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_update_supplier_commits() -> None:
    uow = FakeUow()
    uc = SuppliersUseCases(FakeRepo(), uow)

    uc.update_supplier('s1', {'name': 'N'})

    assert uow.commits == 1


def test_delete_supplier_rolls_back_on_error() -> None:
    uow = FakeUow()
    uc = SuppliersUseCases(FailingRepo(), uow)

    with pytest.raises(RuntimeError):
        uc.delete_supplier('s1')

    assert uow.rollbacks == 1


def test_list_suppliers_delegates_filters() -> None:
    uc = SuppliersUseCases(FakeRepo(), FakeUow())
    result = uc.list_suppliers(SupplierFilters(search='abc'))

    assert result[0]['id'] == 's1'
