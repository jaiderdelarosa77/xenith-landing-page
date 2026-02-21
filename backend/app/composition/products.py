"""Composition root de `products`: conecta casos de uso con adaptadores concretos."""

from app.application.products.use_cases import ProductsUseCases
from app.domain.products.entities import ProductListFilters, ProductSupplierInput, ProductWriteInput
from app.domain.products.errors import (
    CategoryNotFoundError,
    DuplicateSkuError,
    ProductNotFoundError,
    ProductPersistenceError,
    ProductSupplierRelationNotFoundError,
    SupplierNotFoundError,
)
from app.infrastructure.products.sqlalchemy_repository import SqlAlchemyProductsRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _build_use_cases(db):
    return ProductsUseCases(
        products=SqlAlchemyProductsRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )


def _product_payload(product, include_details: bool = False) -> dict:
    payload = {
        'id': product.id,
        'sku': product.sku,
        'name': product.name,
        'description': product.description,
        'categoryId': product.category_id,
        'brand': product.brand,
        'model': product.model,
        'status': product.status,
        'unitPrice': product.unit_price,
        'rentalPrice': product.rental_price,
        'imageUrl': product.image_url,
        'notes': product.notes,
        'deletedAt': product.deleted_at,
        'createdAt': product.created_at,
        'updatedAt': product.updated_at,
        'category': (
            {
                'id': product.category.id,
                'name': product.category.name,
                'color': product.category.color,
            }
            if product.category
            else None
        ),
        '_count': {
            'inventoryItems': product.inventory_count,
        },
    }

    if include_details:
        payload['suppliers'] = [
            {
                'supplierId': rel.supplier_id,
                'supplierSku': rel.supplier_sku,
                'cost': rel.cost,
                'isPreferred': rel.is_preferred,
                'supplier': {
                    'id': rel.supplier.id,
                    'name': rel.supplier.name,
                },
            }
            for rel in product.suppliers
        ]
        payload['inventoryItems'] = [
            {
                'id': item.id,
                'serialNumber': item.serial_number,
                'assetTag': item.asset_tag,
                'status': item.status,
                'condition': item.condition,
                'location': item.location,
            }
            for item in product.inventory_items
        ]

    return payload


def list_products(db, *, search: str, category: str, status_filter: str, include_deleted: bool):
    products = _build_use_cases(db).list_products(
        ProductListFilters(
            search=search,
            category=category,
            status_filter=status_filter,
            include_deleted=include_deleted,
        )
    )
    return [_product_payload(product) for product in products]


def create_product(db, *, payload: dict):
    created = _build_use_cases(db).create_product(
        ProductWriteInput(
            sku=payload['sku'],
            name=payload['name'],
            description=payload.get('description'),
            category_id=payload['categoryId'],
            brand=payload.get('brand'),
            model=payload.get('model'),
            status=payload['status'],
            unit_price=payload.get('unitPrice'),
            rental_price=payload.get('rentalPrice'),
            image_url=payload.get('imageUrl'),
            notes=payload.get('notes'),
        )
    )
    return _product_payload(created)


def get_product(db, product_id: str):
    product = _build_use_cases(db).get_product(product_id)
    return _product_payload(product, include_details=True)


def update_product(db, *, product_id: str, payload: dict):
    updated = _build_use_cases(db).update_product(
        product_id,
        ProductWriteInput(
            sku=payload['sku'],
            name=payload['name'],
            description=payload.get('description'),
            category_id=payload['categoryId'],
            brand=payload.get('brand'),
            model=payload.get('model'),
            status=payload['status'],
            unit_price=payload.get('unitPrice'),
            rental_price=payload.get('rentalPrice'),
            image_url=payload.get('imageUrl'),
            notes=payload.get('notes'),
        ),
    )
    return _product_payload(updated)


def delete_product(db, product_id: str):
    return _build_use_cases(db).delete_product(product_id)


def list_product_suppliers(db, product_id: str):
    rels = _build_use_cases(db).list_product_suppliers(product_id)
    return [
        {
            'productId': rel.product_id,
            'supplierId': rel.supplier_id,
            'supplierSku': rel.supplier_sku,
            'cost': rel.cost,
            'isPreferred': rel.is_preferred,
            'supplier': {
                'id': rel.supplier.id,
                'name': rel.supplier.name,
                'email': rel.supplier.email,
                'phone': rel.supplier.phone,
            },
        }
        for rel in rels
    ]


def add_product_supplier(db, *, product_id: str, payload: dict):
    relation = _build_use_cases(db).add_product_supplier(
        product_id,
        ProductSupplierInput(
            supplier_id=payload['supplierId'],
            supplier_sku=payload.get('supplierSku'),
            cost=payload.get('cost'),
            is_preferred=payload.get('isPreferred', False),
        ),
    )
    return {
        'productId': relation.product_id,
        'supplierId': relation.supplier_id,
        'supplierSku': relation.supplier_sku,
        'cost': relation.cost,
        'isPreferred': relation.is_preferred,
        'supplier': {
            'id': relation.supplier.id,
            'name': relation.supplier.name,
        },
    }


def remove_product_supplier(db, *, product_id: str, supplier_id: str):
    _build_use_cases(db).remove_product_supplier(product_id, supplier_id)
    return {'success': True}


__all__ = [
    'CategoryNotFoundError',
    'DuplicateSkuError',
    'ProductNotFoundError',
    'ProductPersistenceError',
    'ProductSupplierRelationNotFoundError',
    'SupplierNotFoundError',
    'add_product_supplier',
    'create_product',
    'delete_product',
    'get_product',
    'list_product_suppliers',
    'list_products',
    'remove_product_supplier',
    'update_product',
]
