"""Adaptador de infraestructura para `rfid` (persistencia concreta)."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.domain.rfid.entities import DetectionFilters, TagFilters
from app.domain.rfid.errors import (
    DuplicateEpcError,
    InvalidApiKeyError,
    InvalidTimestampError,
    InventoryItemAlreadyLinkedError,
    InventoryItemNotFoundError,
    TagAlreadyLinkedError,
    TagNotFoundError,
)
from app.models.catalog_inventory import InventoryItem, Product, RfidDetection, RfidTag


class SqlAlchemyRfidRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _serialize_tag(self, tag: RfidTag, include_deep: bool = False) -> dict:
        payload = {
            'id': tag.id,
            'epc': tag.epc,
            'tid': tag.tid,
            'inventoryItemId': tag.inventory_item_id,
            'status': tag.status,
            'firstSeenAt': tag.first_seen_at,
            'lastSeenAt': tag.last_seen_at,
            'createdAt': tag.created_at,
            'updatedAt': tag.updated_at,
            'inventoryItem': {
                'id': tag.inventory_item.id,
                'serialNumber': tag.inventory_item.serial_number,
                'assetTag': tag.inventory_item.asset_tag,
                'status': tag.inventory_item.status,
                'location': tag.inventory_item.location,
                'product': {
                    'id': tag.inventory_item.product.id,
                    'sku': tag.inventory_item.product.sku,
                    'name': tag.inventory_item.product.name,
                    'brand': tag.inventory_item.product.brand,
                    'model': tag.inventory_item.product.model,
                }
                if tag.inventory_item and tag.inventory_item.product
                else None,
            }
            if tag.inventory_item
            else None,
            '_count': {
                'detections': len(tag.detections),
            },
        }

        if include_deep:
            payload['detections'] = [
                {
                    'id': detection.id,
                    'readerId': detection.reader_id,
                    'readerName': detection.reader_name,
                    'rssi': detection.rssi,
                    'direction': detection.direction,
                    'timestamp': detection.timestamp,
                }
                for detection in sorted(tag.detections, key=lambda row: row.timestamp, reverse=True)[:50]
            ]

        return payload

    def _load_tag(self, tag_id: str) -> RfidTag | None:
        return self._db.scalar(
            select(RfidTag)
            .where(RfidTag.id == tag_id)
            .options(
                selectinload(RfidTag.inventory_item).selectinload(InventoryItem.product),
                selectinload(RfidTag.detections),
            )
        )

    def _parse_timestamp(self, value: str | None) -> datetime:
        if not value:
            return datetime.utcnow()
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise InvalidTimestampError('Timestamp invalido en lectura RFID') from None

    def list_tags(self, filters: TagFilters) -> list[dict]:
        conditions = []
        if filters.search:
            search_like = f'%{filters.search}%'
            conditions.append(
                or_(
                    RfidTag.epc.ilike(search_like),
                    RfidTag.tid.ilike(search_like),
                    RfidTag.inventory_item.has(InventoryItem.serial_number.ilike(search_like)),
                    RfidTag.inventory_item.has(InventoryItem.asset_tag.ilike(search_like)),
                )
            )

        if filters.status_filter in {'ENROLLED', 'UNASSIGNED', 'UNKNOWN'}:
            conditions.append(RfidTag.status == filters.status_filter)

        stmt = (
            select(RfidTag)
            .options(
                selectinload(RfidTag.inventory_item).selectinload(InventoryItem.product),
                selectinload(RfidTag.detections),
            )
            .order_by(RfidTag.last_seen_at.desc())
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))

        tags = self._db.scalars(stmt).all()
        return [self._serialize_tag(tag) for tag in tags]

    def create_tag(self, payload: dict) -> dict:
        existing = self._db.scalar(select(RfidTag).where(RfidTag.epc == payload['epc']))
        if existing:
            raise DuplicateEpcError('Ya existe un tag con ese EPC')

        inventory_item_id = payload.get('inventoryItemId')
        if inventory_item_id:
            item = self._db.get(InventoryItem, inventory_item_id)
            if not item:
                raise InventoryItemNotFoundError('Item de inventario no encontrado')
            used = self._db.scalar(select(RfidTag).where(RfidTag.inventory_item_id == inventory_item_id))
            if used:
                raise InventoryItemAlreadyLinkedError('El item ya tiene un tag RFID vinculado')

        tag = RfidTag(
            id=str(uuid4()),
            epc=payload['epc'],
            tid=payload.get('tid'),
            inventory_item_id=inventory_item_id,
            status='ENROLLED' if inventory_item_id else payload.get('status', 'UNASSIGNED'),
        )
        self._db.add(tag)
        self._db.flush()

        tag = self._load_tag(tag.id)
        return self._serialize_tag(tag)

    def list_unknown_tags(self) -> list[dict]:
        tags = self._db.scalars(
            select(RfidTag)
            .where(RfidTag.status == 'UNKNOWN')
            .options(selectinload(RfidTag.detections))
            .order_by(RfidTag.last_seen_at.desc())
        ).all()
        return [self._serialize_tag(tag) for tag in tags]

    def get_tag(self, tag_id: str) -> dict:
        tag = self._load_tag(tag_id)
        if not tag:
            raise TagNotFoundError('Tag RFID no encontrado')
        return self._serialize_tag(tag, include_deep=True)

    def update_tag(self, tag_id: str, payload: dict) -> dict:
        tag = self._db.get(RfidTag, tag_id)
        if not tag:
            raise TagNotFoundError('Tag RFID no encontrado')

        duplicate = self._db.scalar(select(RfidTag).where(RfidTag.epc == payload['epc'], RfidTag.id != tag_id))
        if duplicate:
            raise DuplicateEpcError('Ya existe un tag con ese EPC')

        tag.epc = payload['epc']
        tag.tid = payload.get('tid')
        tag.inventory_item_id = payload.get('inventoryItemId')
        tag.status = 'ENROLLED' if payload.get('inventoryItemId') else payload.get('status', 'UNASSIGNED')
        self._db.flush()

        tag = self._load_tag(tag_id)
        return self._serialize_tag(tag)

    def delete_tag(self, tag_id: str) -> dict:
        tag = self._db.get(RfidTag, tag_id)
        if not tag:
            raise TagNotFoundError('Tag RFID no encontrado')

        self._db.delete(tag)
        self._db.flush()
        return {'success': True}

    def enroll_tag(self, tag_id: str, inventory_item_id: str) -> dict:
        tag = self._db.get(RfidTag, tag_id)
        if not tag:
            raise TagNotFoundError('Tag RFID no encontrado')

        if tag.status == 'ENROLLED' and tag.inventory_item_id:
            raise TagAlreadyLinkedError('El tag ya esta vinculado a otro item')

        item = self._db.get(InventoryItem, inventory_item_id)
        if not item:
            raise InventoryItemNotFoundError('Item de inventario no encontrado')

        used = self._db.scalar(select(RfidTag).where(RfidTag.inventory_item_id == inventory_item_id, RfidTag.id != tag_id))
        if used:
            raise InventoryItemAlreadyLinkedError('El item ya tiene un tag RFID vinculado')

        tag.inventory_item_id = inventory_item_id
        tag.status = 'ENROLLED'
        self._db.flush()

        tag = self._load_tag(tag_id)
        return self._serialize_tag(tag)

    def unenroll_tag(self, tag_id: str) -> dict:
        tag = self._db.get(RfidTag, tag_id)
        if not tag:
            raise TagNotFoundError('Tag RFID no encontrado')

        tag.inventory_item_id = None
        tag.status = 'UNASSIGNED'
        self._db.flush()

        tag = self._load_tag(tag_id)
        return self._serialize_tag(tag)

    def list_detections(self, filters: DetectionFilters) -> dict:
        conditions = []
        if filters.rfid_tag_id:
            conditions.append(RfidDetection.rfid_tag_id == filters.rfid_tag_id)
        if filters.reader_id:
            conditions.append(RfidDetection.reader_id == filters.reader_id)
        if filters.direction in {'IN', 'OUT'}:
            conditions.append(RfidDetection.direction == filters.direction)

        stmt = select(RfidDetection).options(
            selectinload(RfidDetection.rfid_tag).selectinload(RfidTag.inventory_item).selectinload(InventoryItem.product)
        )
        count_stmt = select(func.count(RfidDetection.id))

        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        stmt = stmt.order_by(RfidDetection.timestamp.desc()).limit(filters.limit).offset(filters.offset)

        detections = self._db.scalars(stmt).all()
        total = self._db.scalar(count_stmt) or 0

        return {
            'detections': [
                {
                    'id': detection.id,
                    'rfidTagId': detection.rfid_tag_id,
                    'readerId': detection.reader_id,
                    'readerName': detection.reader_name,
                    'rssi': detection.rssi,
                    'direction': detection.direction,
                    'timestamp': detection.timestamp,
                    'rfidTag': {
                        'id': detection.rfid_tag.id,
                        'epc': detection.rfid_tag.epc,
                        'status': detection.rfid_tag.status,
                        'inventoryItem': {
                            'id': detection.rfid_tag.inventory_item.id,
                            'serialNumber': detection.rfid_tag.inventory_item.serial_number,
                            'assetTag': detection.rfid_tag.inventory_item.asset_tag,
                            'product': {
                                'name': detection.rfid_tag.inventory_item.product.name,
                                'sku': detection.rfid_tag.inventory_item.product.sku,
                            }
                            if detection.rfid_tag.inventory_item and detection.rfid_tag.inventory_item.product
                            else None,
                        }
                        if detection.rfid_tag and detection.rfid_tag.inventory_item
                        else None,
                    }
                    if detection.rfid_tag
                    else None,
                }
                for detection in detections
            ],
            'total': total,
            'limit': filters.limit,
            'offset': filters.offset,
        }

    def process_read(self, payload: dict, api_key: str) -> dict:
        if payload['apiKey'] != api_key:
            raise InvalidApiKeyError('API key invalida')

        results = []
        for read in payload['reads']:
            detection_time = self._parse_timestamp(read.get('timestamp'))

            tag = self._db.scalar(select(RfidTag).where(RfidTag.epc == read['epc']).options(selectinload(RfidTag.inventory_item)))
            is_new = False
            inventory_updated = False

            if not tag:
                tag = RfidTag(
                    id=str(uuid4()),
                    epc=read['epc'],
                    tid=read.get('tid'),
                    status='UNKNOWN',
                    first_seen_at=detection_time,
                    last_seen_at=detection_time,
                )
                self._db.add(tag)
                self._db.flush()
                is_new = True
            else:
                tag.last_seen_at = detection_time
                if read.get('tid') and not tag.tid:
                    tag.tid = read.get('tid')

            detection = RfidDetection(
                id=str(uuid4()),
                rfid_tag_id=tag.id,
                reader_id=payload['readerId'],
                reader_name=payload.get('readerName'),
                rssi=read.get('rssi'),
                direction=read.get('direction'),
                timestamp=detection_time,
            )
            self._db.add(detection)

            if tag.status == 'ENROLLED' and tag.inventory_item and read.get('direction') in {'IN', 'OUT'}:
                new_status = 'IN' if read.get('direction') == 'IN' else 'OUT'
                if tag.inventory_item.status != new_status:
                    tag.inventory_item.status = new_status
                    inventory_updated = True

            results.append(
                {
                    'epc': read['epc'],
                    'tagId': tag.id,
                    'status': tag.status,
                    'isNew': is_new,
                    'inventoryItemId': tag.inventory_item_id,
                    'inventoryUpdated': inventory_updated,
                }
            )

        self._db.flush()
        return {'success': True, 'processed': len(results), 'results': results}
