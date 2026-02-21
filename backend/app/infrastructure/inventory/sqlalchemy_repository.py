"""Adaptador de infraestructura para `inventory` (persistencia concreta)."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.domain.inventory.entities import CheckInOutInput, InventoryItemInput, InventoryListFilters, MovementListFilters
from app.domain.inventory.errors import (
    DuplicateAssetTagError,
    DuplicateSerialError,
    InvalidDateFormatError,
    InventoryItemNotFoundError,
    InventoryPersistenceError,
    ProductNotFoundOrInactiveError,
)
from app.domain.inventory.read_models import (
    InventoryCheckInOutResult,
    InventoryItemView,
    InventoryMovementView,
    InventoryMovementsPageView,
    InventoryMutationResult,
    InventorySummaryView,
)
from app.models.catalog_inventory import Category, InventoryItem, InventoryMovement, Product, RfidTag
from app.models.user import User


class SqlAlchemyInventoryRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_float(value):
        return float(value) if value is not None else None

    def _parse_date(self, value: str | None):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise InvalidDateFormatError('Formato de fecha invalido') from None

    def _movement_payload(self, movement: InventoryMovement, user_map: dict[str, dict]) -> InventoryMovementView:
        return {
            'id': movement.id,
            'inventoryItemId': movement.inventory_item_id,
            'type': movement.type,
            'fromStatus': movement.from_status,
            'toStatus': movement.to_status,
            'fromLocation': movement.from_location,
            'toLocation': movement.to_location,
            'reason': movement.reason,
            'reference': movement.reference,
            'performedBy': movement.performed_by,
            'createdAt': movement.created_at,
            'user': user_map.get(movement.performed_by),
        }

    def _item_payload(
        self,
        item: InventoryItem,
        movement_count: int = 0,
        contents_count: int = 0,
        include_details: bool = False,
    ) -> InventoryItemView:
        payload = {
            'id': item.id,
            'productId': item.product_id,
            'serialNumber': item.serial_number,
            'assetTag': item.asset_tag,
            'type': item.type,
            'status': item.status,
            'condition': item.condition,
            'location': item.location,
            'containerId': item.container_id,
            'purchaseDate': item.purchase_date,
            'purchasePrice': self._to_float(item.purchase_price),
            'warrantyExpiry': item.warranty_expiry,
            'notes': item.notes,
            'createdAt': item.created_at,
            'updatedAt': item.updated_at,
            'product': {
                'id': item.product.id,
                'sku': item.product.sku,
                'name': item.product.name,
                'brand': item.product.brand,
                'model': item.product.model,
                'imageUrl': item.product.image_url,
                'unitPrice': self._to_float(item.product.unit_price),
                'rentalPrice': self._to_float(item.product.rental_price),
                'category': {
                    'id': item.product.category.id,
                    'name': item.product.category.name,
                    'color': item.product.category.color,
                }
                if item.product.category
                else None,
            }
            if item.product
            else None,
            'container': {
                'id': item.container.id,
                'assetTag': item.container.asset_tag,
                'serialNumber': item.container.serial_number,
            }
            if item.container
            else None,
            'rfidTag': {
                'id': item.rfid_tag.id,
                'epc': item.rfid_tag.epc,
                'tid': item.rfid_tag.tid,
                'status': item.rfid_tag.status,
                'lastSeenAt': item.rfid_tag.last_seen_at,
                'firstSeenAt': item.rfid_tag.first_seen_at,
            }
            if item.rfid_tag
            else None,
            '_count': {
                'movements': movement_count,
                'contents': contents_count,
            },
        }

        if include_details:
            payload['contents'] = [
                {
                    'id': child.id,
                    'serialNumber': child.serial_number,
                    'assetTag': child.asset_tag,
                    'status': child.status,
                    'product': {
                        'name': child.product.name,
                        'sku': child.product.sku,
                    }
                    if child.product
                    else None,
                }
                for child in item.contents
            ]

        return payload

    def list_items(self, filters: InventoryListFilters) -> list[InventoryItemView]:
        conditions = []

        if filters.search:
            search_like = f'%{filters.search}%'
            conditions.append(
                or_(
                    InventoryItem.serial_number.ilike(search_like),
                    InventoryItem.asset_tag.ilike(search_like),
                    InventoryItem.product.has(Product.name.ilike(search_like)),
                    InventoryItem.product.has(Product.sku.ilike(search_like)),
                )
            )

        if filters.status_filter:
            conditions.append(InventoryItem.status == filters.status_filter)

        if filters.type_filter:
            conditions.append(InventoryItem.type == filters.type_filter)

        if filters.product_id:
            conditions.append(InventoryItem.product_id == filters.product_id)

        if filters.container_id:
            conditions.append(InventoryItem.container_id == filters.container_id)

        stmt = (
            select(InventoryItem)
            .options(
                selectinload(InventoryItem.product).selectinload(Product.category),
                selectinload(InventoryItem.container),
                selectinload(InventoryItem.rfid_tag),
            )
            .order_by(InventoryItem.created_at.desc())
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))

        items = self._db.scalars(stmt).all()
        item_ids = [item.id for item in items]

        movement_counts: dict[str, int] = {}
        contents_counts: dict[str, int] = {}

        if item_ids:
            movement_rows = self._db.execute(
                select(InventoryMovement.inventory_item_id, func.count(InventoryMovement.id))
                .where(InventoryMovement.inventory_item_id.in_(item_ids))
                .group_by(InventoryMovement.inventory_item_id)
            ).all()
            movement_counts = {item_id: count for item_id, count in movement_rows}

            contents_rows = self._db.execute(
                select(InventoryItem.container_id, func.count(InventoryItem.id))
                .where(InventoryItem.container_id.in_(item_ids))
                .group_by(InventoryItem.container_id)
            ).all()
            contents_counts = {item_id: count for item_id, count in contents_rows if item_id}

        return [self._item_payload(item, movement_counts.get(item.id, 0), contents_counts.get(item.id, 0)) for item in items]

    def create_item(self, payload: InventoryItemInput, user_id: str) -> InventoryItemView:
        product = self._db.get(Product, payload.product_id)
        if not product or product.deleted_at is not None:
            raise ProductNotFoundOrInactiveError('Producto no encontrado o inactivo')

        item = InventoryItem(
            id=str(uuid4()),
            product_id=payload.product_id,
            serial_number=payload.serial_number,
            asset_tag=payload.asset_tag,
            type=payload.item_type,
            status=payload.status,
            condition=payload.condition,
            location=payload.location,
            container_id=payload.container_id,
            purchase_date=self._parse_date(payload.purchase_date),
            purchase_price=payload.purchase_price,
            warranty_expiry=self._parse_date(payload.warranty_expiry),
            notes=payload.notes,
        )
        self._db.add(item)

        movement = InventoryMovement(
            id=str(uuid4()),
            inventory_item_id=item.id,
            type='ENROLLMENT',
            to_status=item.status,
            to_location=item.location,
            reason='Registro inicial',
            performed_by=user_id,
        )
        self._db.add(movement)

        try:
            self._db.flush()
        except IntegrityError as exc:
            msg = str(exc).lower()
            if 'serial' in msg:
                raise DuplicateSerialError('Ya existe un item con ese numero de serie') from None
            if 'assettag' in msg:
                raise DuplicateAssetTagError('Ya existe un item con esa etiqueta de activo') from None
            raise InventoryPersistenceError('No se pudo crear el item de inventario') from None

        item = self._db.scalar(
            select(InventoryItem)
            .where(InventoryItem.id == item.id)
            .options(
                selectinload(InventoryItem.product).selectinload(Product.category),
                selectinload(InventoryItem.container),
                selectinload(InventoryItem.rfid_tag),
            )
        )
        return self._item_payload(item, movement_count=1, contents_count=0)

    def summary(self) -> InventorySummaryView:
        by_status_rows = self._db.execute(select(InventoryItem.status, func.count(InventoryItem.id)).group_by(InventoryItem.status)).all()
        by_type_rows = self._db.execute(select(InventoryItem.type, func.count(InventoryItem.id)).group_by(InventoryItem.type)).all()

        status_counts = {'IN': 0, 'OUT': 0, 'MAINTENANCE': 0, 'LOST': 0}
        for status_name, count in by_status_rows:
            if status_name in status_counts:
                status_counts[status_name] = count

        type_counts = {'UNIT': 0, 'CONTAINER': 0}
        for type_name, count in by_type_rows:
            if type_name in type_counts:
                type_counts[type_name] = count

        total = sum(status_counts.values())

        recent_movements = self._db.scalars(
            select(InventoryMovement)
            .options(selectinload(InventoryMovement.inventory_item).selectinload(InventoryItem.product))
            .order_by(InventoryMovement.created_at.desc())
            .limit(10)
        ).all()

        user_ids = {movement.performed_by for movement in recent_movements}
        user_rows = self._db.execute(select(User.id, User.name, User.email).where(User.id.in_(user_ids))).all() if user_ids else []
        user_map = {user_id: {'name': name, 'email': email} for user_id, name, email in user_rows}

        recent_movements_payload = [
            {
                'id': movement.id,
                'type': movement.type,
                'createdAt': movement.created_at,
                'inventoryItem': {
                    'product': {'name': movement.inventory_item.product.name}
                    if movement.inventory_item and movement.inventory_item.product
                    else None,
                    'serialNumber': movement.inventory_item.serial_number if movement.inventory_item else None,
                    'assetTag': movement.inventory_item.asset_tag if movement.inventory_item else None,
                }
                if movement.inventory_item
                else None,
                'user': user_map.get(movement.performed_by),
            }
            for movement in recent_movements
        ]

        category_rows = self._db.execute(
            select(Category.id, Category.name, Category.color, func.count(InventoryItem.id))
            .join(Product, Product.category_id == Category.id)
            .join(InventoryItem, InventoryItem.product_id == Product.id)
            .group_by(Category.id, Category.name, Category.color)
        ).all()

        return {
            'total': total,
            'byStatus': status_counts,
            'byType': type_counts,
            'byCategory': [{'name': name, 'color': color, 'count': count} for _, name, color, count in category_rows],
            'recentMovements': recent_movements_payload,
        }

    def list_movements(self, filters: MovementListFilters) -> InventoryMovementsPageView:
        conditions = []
        if filters.type_filter:
            conditions.append(InventoryMovement.type == filters.type_filter)
        if filters.inventory_item_id:
            conditions.append(InventoryMovement.inventory_item_id == filters.inventory_item_id)

        stmt = select(InventoryMovement).options(selectinload(InventoryMovement.inventory_item).selectinload(InventoryItem.product))
        count_stmt = select(func.count(InventoryMovement.id))

        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        stmt = stmt.order_by(InventoryMovement.created_at.desc()).limit(filters.limit).offset(filters.offset)

        movements = self._db.scalars(stmt).all()
        total = self._db.scalar(count_stmt) or 0

        user_ids = {movement.performed_by for movement in movements}
        user_rows = self._db.execute(select(User.id, User.name, User.email).where(User.id.in_(user_ids))).all() if user_ids else []
        user_map = {user_id: {'id': user_id, 'name': name, 'email': email} for user_id, name, email in user_rows}

        return {
            'movements': [
                {
                    **self._movement_payload(movement, user_map),
                    'inventoryItem': {
                        'id': movement.inventory_item.id,
                        'serialNumber': movement.inventory_item.serial_number,
                        'assetTag': movement.inventory_item.asset_tag,
                        'product': {
                            'name': movement.inventory_item.product.name,
                            'sku': movement.inventory_item.product.sku,
                        }
                        if movement.inventory_item.product
                        else None,
                    }
                    if movement.inventory_item
                    else None,
                }
                for movement in movements
            ],
            'total': total,
            'limit': filters.limit,
            'offset': filters.offset,
        }

    def get_item(self, item_id: str) -> InventoryItemView:
        item = self._db.scalar(
            select(InventoryItem)
            .where(InventoryItem.id == item_id)
            .options(
                selectinload(InventoryItem.product).selectinload(Product.category),
                selectinload(InventoryItem.container),
                selectinload(InventoryItem.contents).selectinload(InventoryItem.product),
                selectinload(InventoryItem.rfid_tag),
            )
        )

        if not item:
            raise InventoryItemNotFoundError('Item de inventario no encontrado')

        movements = self._db.scalars(
            select(InventoryMovement).where(InventoryMovement.inventory_item_id == item_id).order_by(InventoryMovement.created_at.desc()).limit(20)
        ).all()

        user_ids = {movement.performed_by for movement in movements}
        user_rows = self._db.execute(select(User.id, User.name, User.email).where(User.id.in_(user_ids))).all() if user_ids else []
        user_map = {user_id: {'id': user_id, 'name': name, 'email': email} for user_id, name, email in user_rows}

        movement_count = self._db.scalar(select(func.count(InventoryMovement.id)).where(InventoryMovement.inventory_item_id == item_id)) or 0
        contents_count = self._db.scalar(select(func.count(InventoryItem.id)).where(InventoryItem.container_id == item_id)) or 0

        payload = self._item_payload(item, int(movement_count), int(contents_count), include_details=True)
        payload['movements'] = [self._movement_payload(movement, user_map) for movement in movements]
        return payload

    def update_item(self, item_id: str, payload: InventoryItemInput, user_id: str) -> InventoryItemView:
        item = self._db.get(InventoryItem, item_id)
        if not item:
            raise InventoryItemNotFoundError('Item de inventario no encontrado')

        previous_status = item.status
        previous_location = item.location

        item.product_id = payload.product_id
        item.serial_number = payload.serial_number
        item.asset_tag = payload.asset_tag
        item.type = payload.item_type
        item.status = payload.status
        item.condition = payload.condition
        item.location = payload.location
        item.container_id = payload.container_id
        item.purchase_date = self._parse_date(payload.purchase_date)
        item.purchase_price = payload.purchase_price
        item.warranty_expiry = self._parse_date(payload.warranty_expiry)
        item.notes = payload.notes

        if previous_status != item.status or previous_location != item.location:
            self._db.add(
                InventoryMovement(
                    id=str(uuid4()),
                    inventory_item_id=item.id,
                    type='ADJUSTMENT',
                    from_status=previous_status,
                    to_status=item.status,
                    from_location=previous_location,
                    to_location=item.location,
                    reason='Actualizacion manual',
                    performed_by=user_id,
                )
            )

        try:
            self._db.flush()
        except IntegrityError as exc:
            msg = str(exc).lower()
            if 'serial' in msg:
                raise DuplicateSerialError('Ya existe un item con ese numero de serie') from None
            if 'assettag' in msg:
                raise DuplicateAssetTagError('Ya existe un item con esa etiqueta de activo') from None
            raise InventoryPersistenceError('No se pudo actualizar el item de inventario') from None

        item = self._db.scalar(
            select(InventoryItem)
            .where(InventoryItem.id == item.id)
            .options(
                selectinload(InventoryItem.product).selectinload(Product.category),
                selectinload(InventoryItem.container),
                selectinload(InventoryItem.rfid_tag),
            )
        )
        movement_count = self._db.scalar(select(func.count(InventoryMovement.id)).where(InventoryMovement.inventory_item_id == item.id)) or 0
        contents_count = self._db.scalar(select(func.count(InventoryItem.id)).where(InventoryItem.container_id == item.id)) or 0
        return self._item_payload(item, int(movement_count), int(contents_count))

    def delete_item(self, item_id: str) -> InventoryMutationResult:
        item = self._db.get(InventoryItem, item_id)
        if not item:
            raise InventoryItemNotFoundError('Item de inventario no encontrado')

        tag = self._db.scalar(select(RfidTag).where(RfidTag.inventory_item_id == item_id))
        if tag:
            tag.inventory_item_id = None
            tag.status = 'UNASSIGNED'

        self._db.delete(item)
        self._db.flush()
        return {'success': True}

    def check_in(self, item_id: str, payload: CheckInOutInput, user_id: str) -> InventoryCheckInOutResult:
        item = self._db.get(InventoryItem, item_id)
        if not item:
            raise InventoryItemNotFoundError('Item de inventario no encontrado')

        previous_status = item.status
        previous_location = item.location
        item.status = 'IN'
        item.location = payload.location or item.location

        self._db.add(
            InventoryMovement(
                id=str(uuid4()),
                inventory_item_id=item.id,
                type='CHECK_IN',
                from_status=previous_status,
                to_status='IN',
                from_location=previous_location,
                to_location=item.location,
                reason=payload.reason,
                reference=payload.reference,
                performed_by=user_id,
            )
        )

        self._db.flush()

        return {
            'id': item.id,
            'status': item.status,
            'location': item.location,
            'product': {'id': item.product.id, 'sku': item.product.sku, 'name': item.product.name} if item.product else None,
        }

    def check_out(self, item_id: str, payload: CheckInOutInput, user_id: str) -> InventoryCheckInOutResult:
        item = self._db.get(InventoryItem, item_id)
        if not item:
            raise InventoryItemNotFoundError('Item de inventario no encontrado')

        previous_status = item.status
        previous_location = item.location
        item.status = 'OUT'
        item.location = payload.location

        self._db.add(
            InventoryMovement(
                id=str(uuid4()),
                inventory_item_id=item.id,
                type='CHECK_OUT',
                from_status=previous_status,
                to_status='OUT',
                from_location=previous_location,
                to_location=payload.location,
                reason=payload.reason,
                reference=payload.reference,
                performed_by=user_id,
            )
        )

        self._db.flush()

        return {
            'id': item.id,
            'status': item.status,
            'location': item.location,
            'product': {'id': item.product.id, 'sku': item.product.sku, 'name': item.product.name} if item.product else None,
        }
