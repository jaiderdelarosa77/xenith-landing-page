"""Adaptador de infraestructura para `categories` (persistencia concreta)."""

from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.domain.categories.entities import CategoryFilters
from app.domain.categories.errors import CategoryDuplicateNameError, CategoryHasProductsError, CategoryNotFoundError
from app.models.catalog_inventory import Category


class SqlAlchemyCategoriesRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _serialize_category(category: Category, include_products: bool = False) -> dict:
        payload = {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'color': category.color,
            'icon': category.icon,
            'createdAt': category.created_at,
            'updatedAt': category.updated_at,
            '_count': {'products': len(category.products)},
        }
        if include_products:
            payload['products'] = [
                {
                    'id': product.id,
                    'sku': product.sku,
                    'name': product.name,
                    'brand': product.brand,
                    'model': product.model,
                    'status': product.status,
                    'deletedAt': product.deleted_at,
                }
                for product in sorted([row for row in category.products if row.deleted_at is None], key=lambda row: row.name.lower())[:10]
            ]
        return payload

    def list_categories(self, filters: CategoryFilters) -> list[dict]:
        stmt = select(Category).options(selectinload(Category.products)).order_by(Category.name.asc())
        if filters.search:
            search_like = f'%{filters.search}%'
            stmt = stmt.where(or_(Category.name.ilike(search_like), Category.description.ilike(search_like)))
        categories = self._db.scalars(stmt).all()
        return [self._serialize_category(category) for category in categories]

    def create_category(self, payload: dict) -> dict:
        duplicate = self._db.scalar(select(Category).where(Category.name.ilike(payload['name'])))
        if duplicate:
            raise CategoryDuplicateNameError('Ya existe una categoria con ese nombre')

        category = Category(
            id=str(uuid4()),
            name=payload['name'].strip(),
            description=(payload.get('description') or '').strip() or None,
            color=(payload.get('color') or '').strip() or None,
            icon=(payload.get('icon') or '').strip() or None,
        )
        self._db.add(category)
        self._db.flush()

        category = self._db.scalar(select(Category).where(Category.id == category.id).options(selectinload(Category.products)))
        return self._serialize_category(category)

    def get_category(self, category_id: str) -> dict:
        category = self._db.scalar(select(Category).where(Category.id == category_id).options(selectinload(Category.products)))
        if not category:
            raise CategoryNotFoundError('Categoria no encontrada')
        return self._serialize_category(category, include_products=True)

    def update_category(self, category_id: str, payload: dict) -> dict:
        category = self._db.get(Category, category_id)
        if not category:
            raise CategoryNotFoundError('Categoria no encontrada')

        duplicate = self._db.scalar(select(Category).where(Category.id != category_id, Category.name.ilike(payload['name'])))
        if duplicate:
            raise CategoryDuplicateNameError('Ya existe una categoria con ese nombre')

        category.name = payload['name'].strip()
        category.description = (payload.get('description') or '').strip() or None
        category.color = (payload.get('color') or '').strip() or None
        category.icon = (payload.get('icon') or '').strip() or None
        self._db.flush()

        category = self._db.scalar(select(Category).where(Category.id == category_id).options(selectinload(Category.products)))
        return self._serialize_category(category)

    def delete_category(self, category_id: str) -> dict:
        category = self._db.scalar(select(Category).where(Category.id == category_id).options(selectinload(Category.products)))
        if not category:
            raise CategoryNotFoundError('Categoria no encontrada')
        if len(category.products) > 0:
            raise CategoryHasProductsError('No se puede eliminar la categoria porque tiene productos asociados')

        self._db.delete(category)
        self._db.flush()
        return {'success': True}
