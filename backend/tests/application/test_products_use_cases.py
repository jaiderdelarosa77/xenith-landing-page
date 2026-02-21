from datetime import datetime

import pytest

from app.application.products.use_cases import ProductsUseCases
from app.domain.products.entities import (
    CategoryData,
    ProductData,
    ProductListFilters,
    ProductSupplierInput,
    ProductWriteInput,
)
from app.domain.products.errors import (
    CategoryNotFoundError,
    ProductNotFoundError,
    ProductSupplierRelationNotFoundError,
    SupplierNotFoundError,
)


def _product_data(product_id: str = 'p1') -> ProductData:
    now = datetime.now()
    return ProductData(
        id=product_id,
        sku='SKU-1',
        name='Product',
        description=None,
        category_id='cat-1',
        brand=None,
        model=None,
        status='ACTIVE',
        unit_price=None,
        rental_price=None,
        image_url=None,
        notes=None,
        deleted_at=None,
        created_at=now,
        updated_at=now,
        category=CategoryData(id='cat-1', name='Categoria', color=None),
        inventory_count=0,
        suppliers=[],
        inventory_items=[],
    )


class FakeRepo:
    def __init__(self):
        self.has_category = True
        self.existing_product = _product_data()
        self.has_supplier = True
        self.has_product = True
        self.remove_relation_result = True

    def list_products(self, filters: ProductListFilters):
        return [_product_data()]

    def category_exists(self, category_id: str) -> bool:
        return self.has_category

    def create_product(self, payload: ProductWriteInput):
        return _product_data('p2')

    def get_product(self, product_id: str, include_details: bool):
        return self.existing_product

    def update_product(self, product_id: str, payload: ProductWriteInput):
        return _product_data(product_id)

    def delete_product(self, product_id: str):
        return {'success': True}

    def list_product_suppliers(self, product_id: str):
        return []

    def product_exists(self, product_id: str) -> bool:
        return self.has_product

    def supplier_exists(self, supplier_id: str) -> bool:
        return self.has_supplier

    def upsert_product_supplier(self, product_id: str, payload: ProductSupplierInput):
        return {'productId': product_id, 'supplierId': payload.supplier_id}

    def remove_product_supplier(self, product_id: str, supplier_id: str) -> bool:
        return self.remove_relation_result


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def _write_input() -> ProductWriteInput:
    return ProductWriteInput(
        sku='SKU-1',
        name='Product',
        description=None,
        category_id='cat-1',
        brand=None,
        model=None,
        status='ACTIVE',
        unit_price=None,
        rental_price=None,
        image_url=None,
        notes=None,
    )


def test_create_product_requires_existing_category() -> None:
    repo = FakeRepo()
    repo.has_category = False
    uc = ProductsUseCases(repo, FakeUow())

    with pytest.raises(CategoryNotFoundError):
        uc.create_product(_write_input())


def test_update_product_requires_existing_product() -> None:
    repo = FakeRepo()
    repo.existing_product = None
    uc = ProductsUseCases(repo, FakeUow())

    with pytest.raises(ProductNotFoundError):
        uc.update_product('p1', _write_input())


def test_add_product_supplier_requires_supplier() -> None:
    repo = FakeRepo()
    repo.has_supplier = False
    uc = ProductsUseCases(repo, FakeUow())

    with pytest.raises(SupplierNotFoundError):
        uc.add_product_supplier('p1', ProductSupplierInput('s1', None, None, False))


def test_remove_product_supplier_raises_when_relation_missing() -> None:
    repo = FakeRepo()
    repo.remove_relation_result = False
    uow = FakeUow()
    uc = ProductsUseCases(repo, uow)

    with pytest.raises(ProductSupplierRelationNotFoundError):
        uc.remove_product_supplier('p1', 's1')

    assert uow.rollbacks == 1
