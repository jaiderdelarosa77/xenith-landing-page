"""Adaptador de infraestructura para `suppliers` (persistencia concreta)."""

from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.domain.suppliers.entities import SupplierFilters
from app.domain.suppliers.errors import SupplierHasProductsError, SupplierNotFoundError
from app.models.catalog_inventory import ProductSupplier, Supplier


class SqlAlchemySuppliersRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _serialize_supplier(supplier: Supplier, include_products: bool = False) -> dict:
        payload = {
            'id': supplier.id,
            'name': supplier.name,
            'nit': supplier.nit,
            'contactName': supplier.contact_name,
            'email': supplier.email,
            'phone': supplier.phone,
            'address': supplier.address,
            'city': supplier.city,
            'country': supplier.country,
            'website': supplier.website,
            'notes': supplier.notes,
            'rutUrl': supplier.rut_url,
            'createdAt': supplier.created_at,
            'updatedAt': supplier.updated_at,
            '_count': {'products': len(supplier.products)},
        }
        if include_products:
            payload['products'] = [
                {
                    'productId': link.product_id,
                    'supplierSku': link.supplier_sku,
                    'cost': float(link.cost) if link.cost is not None else None,
                    'isPreferred': link.is_preferred,
                    'product': {
                        'id': link.product.id,
                        'sku': link.product.sku,
                        'name': link.product.name,
                        'brand': link.product.brand,
                    }
                    if link.product
                    else None,
                }
                for link in supplier.products[:10]
            ]
        return payload

    @staticmethod
    def _normalize(payload: dict) -> dict:
        return {
            'name': payload['name'].strip(),
            'nit': (payload.get('nit') or '').strip() or None,
            'contact_name': (payload.get('contactName') or '').strip() or None,
            'email': (payload.get('email') or '').strip() or None,
            'phone': (payload.get('phone') or '').strip() or None,
            'address': (payload.get('address') or '').strip() or None,
            'city': (payload.get('city') or '').strip() or None,
            'country': (payload.get('country') or '').strip() or None,
            'website': (payload.get('website') or '').strip() or None,
            'notes': (payload.get('notes') or '').strip() or None,
            'rut_url': (payload.get('rutUrl') or '').strip() or None,
        }

    def list_suppliers(self, filters: SupplierFilters) -> list[dict]:
        stmt = select(Supplier).options(selectinload(Supplier.products)).order_by(Supplier.name.asc())
        if filters.search:
            search_like = f'%{filters.search}%'
            stmt = stmt.where(or_(Supplier.name.ilike(search_like), Supplier.contact_name.ilike(search_like), Supplier.email.ilike(search_like)))
        suppliers = self._db.scalars(stmt).all()
        return [self._serialize_supplier(supplier) for supplier in suppliers]

    def create_supplier(self, payload: dict) -> dict:
        supplier = Supplier(id=str(uuid4()), **self._normalize(payload))
        self._db.add(supplier)
        self._db.flush()

        supplier = self._db.scalar(select(Supplier).where(Supplier.id == supplier.id).options(selectinload(Supplier.products)))
        return self._serialize_supplier(supplier)

    def get_supplier(self, supplier_id: str) -> dict:
        supplier = self._db.scalar(
            select(Supplier).where(Supplier.id == supplier_id).options(selectinload(Supplier.products).selectinload(ProductSupplier.product))
        )
        if not supplier:
            raise SupplierNotFoundError('Contratista no encontrado')
        return self._serialize_supplier(supplier, include_products=True)

    def update_supplier(self, supplier_id: str, payload: dict) -> dict:
        supplier = self._db.get(Supplier, supplier_id)
        if not supplier:
            raise SupplierNotFoundError('Contratista no encontrado')

        normalized = self._normalize(payload)
        for field, value in normalized.items():
            setattr(supplier, field, value)
        self._db.flush()

        supplier = self._db.scalar(select(Supplier).where(Supplier.id == supplier_id).options(selectinload(Supplier.products)))
        return self._serialize_supplier(supplier)

    def delete_supplier(self, supplier_id: str) -> dict:
        supplier = self._db.scalar(select(Supplier).where(Supplier.id == supplier_id).options(selectinload(Supplier.products)))
        if not supplier:
            raise SupplierNotFoundError('Contratista no encontrado')
        if len(supplier.products) > 0:
            raise SupplierHasProductsError('No se puede eliminar el contratista porque tiene productos asociados')

        self._db.delete(supplier)
        self._db.flush()
        return {'success': True}
