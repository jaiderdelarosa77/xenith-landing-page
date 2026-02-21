"""Adaptador de infraestructura para `item_groups` (persistencia concreta)."""

from uuid import uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, selectinload

from app.domain.item_groups.entities import ItemGroupFilters
from app.domain.item_groups.errors import (
    InventoryItemNotFoundError,
    ItemAlreadyInGroupError,
    ItemGroupNotFoundError,
    ItemNotInGroupError,
)
from app.models.catalog_inventory import InventoryItem, Product
from app.models.project_client import ItemGroup, ItemGroupItem


class SqlAlchemyItemGroupsRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _serialize_group(group: ItemGroup) -> dict:
        items = sorted(group.items, key=lambda row: row.created_at)
        return {
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'createdAt': group.created_at,
            'updatedAt': group.updated_at,
            'items': [
                {
                    'id': group_item.id,
                    'groupId': group_item.group_id,
                    'inventoryItemId': group_item.inventory_item_id,
                    'quantity': group_item.quantity,
                    'notes': group_item.notes,
                    'createdAt': group_item.created_at,
                    'inventoryItem': {
                        'id': group_item.inventory_item.id,
                        'serialNumber': group_item.inventory_item.serial_number,
                        'assetTag': group_item.inventory_item.asset_tag,
                        'status': group_item.inventory_item.status,
                        'location': group_item.inventory_item.location,
                        'product': {
                            'id': group_item.inventory_item.product.id,
                            'sku': group_item.inventory_item.product.sku,
                            'name': group_item.inventory_item.product.name,
                            'brand': group_item.inventory_item.product.brand,
                            'model': group_item.inventory_item.product.model,
                            'rentalPrice': float(group_item.inventory_item.product.rental_price)
                            if group_item.inventory_item.product.rental_price is not None
                            else None,
                            'category': {
                                'id': group_item.inventory_item.product.category.id,
                                'name': group_item.inventory_item.product.category.name,
                                'color': group_item.inventory_item.product.category.color,
                            }
                            if group_item.inventory_item.product and group_item.inventory_item.product.category
                            else None,
                        }
                        if group_item.inventory_item and group_item.inventory_item.product
                        else None,
                    }
                    if group_item.inventory_item
                    else None,
                }
                for group_item in items
            ],
            '_count': {'items': len(items)},
        }

    @staticmethod
    def _group_stmt(group_id: str | None = None):
        stmt = select(ItemGroup).options(
            selectinload(ItemGroup.items)
            .selectinload(ItemGroupItem.inventory_item)
            .selectinload(InventoryItem.product)
            .selectinload(Product.category)
        )
        if group_id:
            stmt = stmt.where(ItemGroup.id == group_id)
        return stmt

    def list_groups(self, filters: ItemGroupFilters) -> list[dict]:
        conditions = []
        if filters.search:
            search_like = f'%{filters.search}%'
            conditions.append(or_(ItemGroup.name.ilike(search_like), ItemGroup.description.ilike(search_like)))

        stmt = self._group_stmt().order_by(ItemGroup.created_at.desc())
        if conditions:
            stmt = stmt.where(and_(*conditions))

        groups = self._db.scalars(stmt).all()
        return [self._serialize_group(group) for group in groups]

    def create_group(self, payload: dict) -> dict:
        group = ItemGroup(
            id=str(uuid4()),
            name=payload['name'].strip(),
            description=(payload.get('description') or '').strip() or None,
        )
        self._db.add(group)
        self._db.flush()

        group = self._db.scalar(self._group_stmt(group.id))
        return self._serialize_group(group)

    def get_group(self, group_id: str) -> dict:
        group = self._db.scalar(self._group_stmt(group_id))
        if not group:
            raise ItemGroupNotFoundError('Grupo no encontrado')
        return self._serialize_group(group)

    def update_group(self, group_id: str, payload: dict) -> dict:
        group = self._db.get(ItemGroup, group_id)
        if not group:
            raise ItemGroupNotFoundError('Grupo no encontrado')

        group.name = payload['name'].strip()
        group.description = (payload.get('description') or '').strip() or None
        self._db.flush()

        group = self._db.scalar(self._group_stmt(group_id))
        return self._serialize_group(group)

    def delete_group(self, group_id: str) -> dict:
        group = self._db.get(ItemGroup, group_id)
        if not group:
            raise ItemGroupNotFoundError('Grupo no encontrado')

        self._db.delete(group)
        self._db.flush()
        return {'message': 'Grupo eliminado exitosamente'}

    def add_item(self, group_id: str, payload: dict) -> dict:
        group = self._db.get(ItemGroup, group_id)
        if not group:
            raise ItemGroupNotFoundError('Grupo no encontrado')

        inventory_item = self._db.get(InventoryItem, payload['inventoryItemId'])
        if not inventory_item:
            raise InventoryItemNotFoundError('Item de inventario no encontrado')

        existing = self._db.scalar(
            select(ItemGroupItem).where(
                ItemGroupItem.group_id == group_id,
                ItemGroupItem.inventory_item_id == payload['inventoryItemId'],
            )
        )
        if existing:
            raise ItemAlreadyInGroupError('Este item ya esta en el grupo')

        self._db.add(
            ItemGroupItem(
                id=str(uuid4()),
                group_id=group_id,
                inventory_item_id=payload['inventoryItemId'],
                quantity=payload['quantity'],
                notes=(payload.get('notes') or '').strip() or None,
            )
        )
        self._db.flush()

        updated_group = self._db.scalar(self._group_stmt(group_id))
        return self._serialize_group(updated_group)

    def remove_item(self, group_id: str, item_id: str) -> dict:
        group_item = self._db.scalar(
            select(ItemGroupItem).where(ItemGroupItem.group_id == group_id, ItemGroupItem.inventory_item_id == item_id)
        )
        if not group_item:
            raise ItemNotInGroupError('Item no encontrado en el grupo')

        self._db.delete(group_item)
        self._db.flush()

        updated_group = self._db.scalar(self._group_stmt(group_id))
        return self._serialize_group(updated_group)
