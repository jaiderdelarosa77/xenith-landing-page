"""Casos de uso de `products`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.products.entities import ProductListFilters, ProductSupplierInput, ProductWriteInput
from app.domain.products.errors import (
    CategoryNotFoundError,
    ProductNotFoundError,
    ProductSupplierRelationNotFoundError,
    SupplierNotFoundError,
)
from app.domain.products.ports import ProductsRepository, UnitOfWork


class ProductsUseCases:
    def __init__(self, products: ProductsRepository, uow: UnitOfWork) -> None:
        self._products = products
        self._uow = uow

    def list_products(self, filters: ProductListFilters):
        return self._products.list_products(filters)

    def create_product(self, payload: ProductWriteInput):
        if not self._products.category_exists(payload.category_id):
            raise CategoryNotFoundError('La categoria no existe')
        try:
            created = self._products.create_product(payload)
            self._uow.commit()
            return created
        except Exception:
            self._uow.rollback()
            raise

    def get_product(self, product_id: str):
        product = self._products.get_product(product_id, include_details=True)
        if not product:
            raise ProductNotFoundError('Producto no encontrado')
        return product

    def update_product(self, product_id: str, payload: ProductWriteInput):
        if not self._products.get_product(product_id, include_details=False):
            raise ProductNotFoundError('Producto no encontrado')
        if not self._products.category_exists(payload.category_id):
            raise CategoryNotFoundError('La categoria no existe')
        try:
            updated = self._products.update_product(product_id, payload)
            if not updated:
                raise ProductNotFoundError('Producto no encontrado')
            self._uow.commit()
            return updated
        except Exception:
            self._uow.rollback()
            raise

    def delete_product(self, product_id: str):
        try:
            result = self._products.delete_product(product_id)
            if result is None:
                raise ProductNotFoundError('Producto no encontrado')
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def list_product_suppliers(self, product_id: str):
        return self._products.list_product_suppliers(product_id)

    def add_product_supplier(self, product_id: str, payload: ProductSupplierInput):
        if not self._products.product_exists(product_id):
            raise ProductNotFoundError('Producto no encontrado')
        if not self._products.supplier_exists(payload.supplier_id):
            raise SupplierNotFoundError('Proveedor no encontrado')
        try:
            relation = self._products.upsert_product_supplier(product_id, payload)
            self._uow.commit()
            return relation
        except Exception:
            self._uow.rollback()
            raise

    def remove_product_supplier(self, product_id: str, supplier_id: str):
        try:
            removed = self._products.remove_product_supplier(product_id, supplier_id)
            if not removed:
                raise ProductSupplierRelationNotFoundError('Relacion producto-proveedor no encontrada')
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
