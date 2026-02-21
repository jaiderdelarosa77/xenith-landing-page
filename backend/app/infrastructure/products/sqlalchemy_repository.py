"""Adaptador de infraestructura para `products` (persistencia concreta)."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.domain.products.entities import (
    CategoryData,
    InventoryItemLite,
    ProductData,
    ProductListFilters,
    ProductSupplierData,
    ProductSupplierInput,
    ProductWriteInput,
    SupplierLite,
)
from app.domain.products.errors import DuplicateSkuError, ProductPersistenceError
from app.models.catalog_inventory import Category, InventoryItem, Product, ProductSupplier, Supplier


class SqlAlchemyProductsRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_products(self, filters: ProductListFilters) -> list[ProductData]:
        conditions = []
        if not filters.include_deleted:
            conditions.append(Product.deleted_at.is_(None))

        if filters.search:
            search_like = f'%{filters.search}%'
            conditions.append(
                or_(
                    Product.name.ilike(search_like),
                    Product.sku.ilike(search_like),
                    Product.brand.ilike(search_like),
                    Product.model.ilike(search_like),
                )
            )

        if filters.category:
            conditions.append(Product.category_id == filters.category)

        if filters.status_filter in {'ACTIVE', 'INACTIVE'}:
            conditions.append(Product.status == filters.status_filter)

        stmt = select(Product).options(selectinload(Product.category)).order_by(Product.name.asc())
        if conditions:
            stmt = stmt.where(and_(*conditions))

        products = self._db.scalars(stmt).all()
        product_ids = [product.id for product in products]

        counts: dict[str, int] = {}
        if product_ids:
            count_rows = self._db.execute(
                select(InventoryItem.product_id, func.count(InventoryItem.id))
                .where(InventoryItem.product_id.in_(product_ids))
                .group_by(InventoryItem.product_id)
            ).all()
            counts = {product_id: count for product_id, count in count_rows}

        return [self._to_product_data(product, int(counts.get(product.id, 0))) for product in products]

    def category_exists(self, category_id: str) -> bool:
        return self._db.get(Category, category_id) is not None

    def create_product(self, payload: ProductWriteInput) -> ProductData:
        product = Product(
            id=str(uuid4()),
            sku=payload.sku,
            name=payload.name,
            description=payload.description,
            category_id=payload.category_id,
            brand=payload.brand,
            model=payload.model,
            status=payload.status,
            unit_price=payload.unit_price,
            rental_price=payload.rental_price,
            image_url=payload.image_url,
            notes=payload.notes,
        )

        self._db.add(product)
        try:
            self._db.flush()
        except IntegrityError as exc:
            if 'sku' in str(exc).lower():
                raise DuplicateSkuError('Ya existe un producto con ese SKU') from None
            raise ProductPersistenceError('No se pudo crear el producto') from None

        self._db.refresh(product)
        self._db.refresh(product, attribute_names=['category'])
        return self._to_product_data(product, inventory_count=0)

    def get_product(self, product_id: str, include_details: bool) -> ProductData | None:
        options = [selectinload(Product.category)]
        if include_details:
            options.extend(
                [
                    selectinload(Product.suppliers).selectinload(ProductSupplier.supplier),
                    selectinload(Product.inventory_items),
                ]
            )

        product = self._db.scalar(select(Product).where(Product.id == product_id).options(*options))
        if not product:
            return None

        inventory_count = self._db.scalar(select(func.count(InventoryItem.id)).where(InventoryItem.product_id == product_id)) or 0
        data = self._to_product_data(product, int(inventory_count))

        if include_details:
            data.suppliers = [self._to_product_supplier(rel) for rel in product.suppliers]
            data.inventory_items = [
                InventoryItemLite(
                    id=item.id,
                    serial_number=item.serial_number,
                    asset_tag=item.asset_tag,
                    status=item.status,
                    condition=item.condition,
                    location=item.location,
                )
                for item in sorted(product.inventory_items, key=lambda row: row.created_at, reverse=True)[:10]
            ]

        return data

    def update_product(self, product_id: str, payload: ProductWriteInput) -> ProductData | None:
        product = self._db.get(Product, product_id)
        if not product:
            return None

        product.sku = payload.sku
        product.name = payload.name
        product.description = payload.description
        product.category_id = payload.category_id
        product.brand = payload.brand
        product.model = payload.model
        product.status = payload.status
        product.unit_price = payload.unit_price
        product.rental_price = payload.rental_price
        product.image_url = payload.image_url
        product.notes = payload.notes

        try:
            self._db.flush()
        except IntegrityError as exc:
            if 'sku' in str(exc).lower():
                raise DuplicateSkuError('Ya existe un producto con ese SKU') from None
            raise ProductPersistenceError('No se pudo actualizar el producto') from None

        self._db.refresh(product)
        self._db.refresh(product, attribute_names=['category'])
        inventory_count = self._db.scalar(select(func.count(InventoryItem.id)).where(InventoryItem.product_id == product_id)) or 0
        return self._to_product_data(product, int(inventory_count))

    def delete_product(self, product_id: str) -> dict | None:
        product = self._db.get(Product, product_id)
        if not product:
            return None

        inventory_count = self._db.scalar(select(func.count(InventoryItem.id)).where(InventoryItem.product_id == product_id)) or 0
        if inventory_count > 0:
            product.deleted_at = datetime.utcnow()
            self._db.flush()
            return {'success': True, 'softDeleted': True}

        self._db.delete(product)
        self._db.flush()
        return {'success': True}

    def list_product_suppliers(self, product_id: str) -> list[ProductSupplierData]:
        rels = self._db.scalars(
            select(ProductSupplier)
            .where(ProductSupplier.product_id == product_id)
            .options(selectinload(ProductSupplier.supplier))
            .order_by(ProductSupplier.is_preferred.desc())
        ).all()
        return [self._to_product_supplier(rel) for rel in rels]

    def product_exists(self, product_id: str) -> bool:
        return self._db.get(Product, product_id) is not None

    def supplier_exists(self, supplier_id: str) -> bool:
        return self._db.get(Supplier, supplier_id) is not None

    def upsert_product_supplier(self, product_id: str, payload: ProductSupplierInput) -> ProductSupplierData:
        relation = self._db.get(ProductSupplier, {'product_id': product_id, 'supplier_id': payload.supplier_id})
        if relation:
            relation.supplier_sku = payload.supplier_sku
            relation.cost = payload.cost
            relation.is_preferred = payload.is_preferred
        else:
            relation = ProductSupplier(
                product_id=product_id,
                supplier_id=payload.supplier_id,
                supplier_sku=payload.supplier_sku,
                cost=payload.cost,
                is_preferred=payload.is_preferred,
            )
            self._db.add(relation)

        self._db.flush()
        self._db.refresh(relation)
        self._db.refresh(relation, attribute_names=['supplier'])
        return self._to_product_supplier(relation)

    def remove_product_supplier(self, product_id: str, supplier_id: str) -> bool:
        relation = self._db.get(ProductSupplier, {'product_id': product_id, 'supplier_id': supplier_id})
        if not relation:
            return False
        self._db.delete(relation)
        self._db.flush()
        return True

    @staticmethod
    def _to_float(value):
        return float(value) if value is not None else None

    def _to_product_data(self, product: Product, inventory_count: int) -> ProductData:
        category = None
        if product.category:
            category = CategoryData(id=product.category.id, name=product.category.name, color=product.category.color)

        return ProductData(
            id=product.id,
            sku=product.sku,
            name=product.name,
            description=product.description,
            category_id=product.category_id,
            brand=product.brand,
            model=product.model,
            status=product.status,
            unit_price=self._to_float(product.unit_price),
            rental_price=self._to_float(product.rental_price),
            image_url=product.image_url,
            notes=product.notes,
            deleted_at=product.deleted_at,
            created_at=product.created_at,
            updated_at=product.updated_at,
            category=category,
            inventory_count=inventory_count,
            suppliers=[],
            inventory_items=[],
        )

    def _to_product_supplier(self, rel: ProductSupplier) -> ProductSupplierData:
        supplier = SupplierLite(
            id=rel.supplier.id,
            name=rel.supplier.name,
            email=rel.supplier.email,
            phone=rel.supplier.phone,
        )
        return ProductSupplierData(
            product_id=rel.product_id,
            supplier_id=rel.supplier_id,
            supplier_sku=rel.supplier_sku,
            cost=self._to_float(rel.cost),
            is_preferred=rel.is_preferred,
            supplier=supplier,
        )
