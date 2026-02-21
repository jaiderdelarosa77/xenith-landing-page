"""Adaptador de infraestructura para `quotations` (persistencia concreta)."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.orm import Session, selectinload

from app.domain.quotations.entities import QuotationFilters
from app.domain.quotations.errors import (
    ClientNotFoundError,
    EmptyQuotationError,
    InvalidValidUntilError,
    ItemGroupNotFoundError,
    ProjectNotFoundError,
    QuotationNotFoundError,
)
from app.domain.quotations.read_models import QuotationMutationResult, QuotationPayload, QuotationView
from app.models.catalog_inventory import InventoryItem, Product
from app.models.project_client import Client, ItemGroup, ItemGroupItem, Project, Quotation, QuotationGroup, QuotationItem


class SqlAlchemyQuotationsRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _dec(value) -> float:
        if value is None:
            return 0.0
        return float(value)

    def _parse_date(self, value: str) -> datetime:
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise InvalidValidUntilError('Fecha de validez invalida') from None

    def _serialize_quotation(self, quotation: Quotation, include_deep: bool = False) -> QuotationView:
        payload = {
            'id': quotation.id,
            'quotationNumber': quotation.quotation_number,
            'title': quotation.title,
            'description': quotation.description,
            'clientId': quotation.client_id,
            'projectId': quotation.project_id,
            'createdBy': quotation.created_by,
            'status': quotation.status,
            'validUntil': quotation.valid_until,
            'subtotal': self._dec(quotation.subtotal),
            'tax': self._dec(quotation.tax),
            'discount': self._dec(quotation.discount),
            'total': self._dec(quotation.total),
            'notes': quotation.notes,
            'terms': quotation.terms,
            'createdAt': quotation.created_at,
            'updatedAt': quotation.updated_at,
            'client': {
                'id': quotation.client.id,
                'name': quotation.client.name,
                'company': quotation.client.company,
                'email': quotation.client.email,
                'phone': quotation.client.phone,
                'address': quotation.client.address,
                'city': quotation.client.city,
                'country': quotation.client.country,
                'taxId': quotation.client.nit,
            }
            if quotation.client
            else None,
            'project': {
                'id': quotation.project.id,
                'title': quotation.project.title,
                'description': quotation.project.description,
            }
            if quotation.project
            else None,
            'createdByUser': {
                'id': quotation.created_by_user.id,
                'name': quotation.created_by_user.name,
                'email': quotation.created_by_user.email,
            }
            if quotation.created_by_user
            else None,
        }

        items = sorted(quotation.items, key=lambda row: row.order)
        payload['items'] = [
            {
                'id': item.id,
                'quotationId': item.quotation_id,
                'inventoryItemId': item.inventory_item_id,
                'description': item.description,
                'quantity': item.quantity,
                'unitPrice': self._dec(item.unit_price),
                'total': self._dec(item.total),
                'order': item.order,
                'createdAt': item.created_at,
                'updatedAt': item.updated_at,
                'inventoryItem': {
                    'id': item.inventory_item.id,
                    'serialNumber': item.inventory_item.serial_number,
                    'assetTag': item.inventory_item.asset_tag,
                    'product': {
                        'id': item.inventory_item.product.id,
                        'sku': item.inventory_item.product.sku,
                        'name': item.inventory_item.product.name,
                        'brand': item.inventory_item.product.brand,
                        'model': item.inventory_item.product.model,
                    }
                    if item.inventory_item and item.inventory_item.product
                    else None,
                }
                if include_deep and item.inventory_item
                else None,
            }
            for item in items
        ]

        groups = sorted(quotation.groups, key=lambda row: row.order)
        payload['groups'] = [
            {
                'id': group.id,
                'quotationId': group.quotation_id,
                'groupId': group.group_id,
                'name': group.name,
                'description': group.description,
                'unitPrice': self._dec(group.unit_price),
                'quantity': group.quantity,
                'total': self._dec(group.total),
                'order': group.order,
                'createdAt': group.created_at,
                'updatedAt': group.updated_at,
                'group': {
                    'id': group.group.id,
                    'name': group.group.name,
                    'description': group.group.description,
                    'items': [
                        {
                            'id': group_item.id,
                            'inventoryItem': {
                                'id': group_item.inventory_item.id,
                                'serialNumber': group_item.inventory_item.serial_number,
                                'assetTag': group_item.inventory_item.asset_tag,
                                'product': {
                                    'id': group_item.inventory_item.product.id,
                                    'sku': group_item.inventory_item.product.sku,
                                    'name': group_item.inventory_item.product.name,
                                    'brand': group_item.inventory_item.product.brand,
                                    'model': group_item.inventory_item.product.model,
                                    'category': {
                                        'id': group_item.inventory_item.product.category.id,
                                        'name': group_item.inventory_item.product.category.name,
                                        'color': group_item.inventory_item.product.category.color,
                                    }
                                    if group_item.inventory_item.product.category
                                    else None,
                                }
                                if group_item.inventory_item.product
                                else None,
                            }
                            if group_item.inventory_item
                            else None,
                        }
                        for group_item in group.group.items
                    ]
                    if include_deep
                    else None,
                }
                if group.group
                else None,
            }
            for group in groups
        ]

        return payload

    def _generate_quotation_number(self) -> str:
        year = datetime.utcnow().year
        prefix = f'QT-{year}-'

        last = self._db.scalar(
            select(Quotation).where(Quotation.quotation_number.like(f'{prefix}%')).order_by(Quotation.quotation_number.desc())
        )

        if not last:
            return f'{prefix}0001'

        last_number = int(last.quotation_number.split('-')[2])
        return f'{prefix}{str(last_number + 1).zfill(4)}'

    def _calculate_totals(self, payload: QuotationPayload):
        subtotal = Decimal('0')

        parsed_items = []
        for index, item in enumerate(payload.get('items') or []):
            item_total = Decimal(item['quantity']) * Decimal(str(item['unitPrice']))
            subtotal += item_total
            parsed_items.append(
                {
                    'inventoryItemId': item.get('inventoryItemId'),
                    'description': item['description'],
                    'quantity': item['quantity'],
                    'unitPrice': Decimal(str(item['unitPrice'])),
                    'total': item_total,
                    'order': index,
                }
            )

        parsed_groups = []
        for index, group in enumerate(payload.get('groups') or []):
            group_total = Decimal(group['quantity']) * Decimal(str(group['unitPrice']))
            subtotal += group_total
            parsed_groups.append(
                {
                    'groupId': group['groupId'],
                    'name': group['name'],
                    'description': group.get('description'),
                    'unitPrice': Decimal(str(group['unitPrice'])),
                    'quantity': group['quantity'],
                    'total': group_total,
                    'order': len(parsed_items) + index,
                }
            )

        discount = Decimal(payload.get('discount') or '0')
        tax_rate = Decimal(payload.get('tax') or '16')
        subtotal_after_discount = subtotal - discount
        tax_value = subtotal_after_discount * tax_rate / Decimal('100')
        total = subtotal_after_discount + tax_value

        return parsed_items, parsed_groups, subtotal, discount, tax_value, total

    def list_quotations(self, filters: QuotationFilters) -> list[QuotationView]:
        conditions = []
        if filters.search:
            search_like = f'%{filters.search}%'
            conditions.append(or_(Quotation.title.ilike(search_like), Quotation.quotation_number.ilike(search_like)))
        if filters.status_filter:
            conditions.append(Quotation.status == filters.status_filter)
        if filters.client_id:
            conditions.append(Quotation.client_id == filters.client_id)
        if filters.project_id:
            conditions.append(Quotation.project_id == filters.project_id)

        stmt = (
            select(Quotation)
            .options(
                selectinload(Quotation.client),
                selectinload(Quotation.project),
                selectinload(Quotation.created_by_user),
                selectinload(Quotation.items),
                selectinload(Quotation.groups).selectinload(QuotationGroup.group),
            )
            .order_by(Quotation.created_at.desc())
        )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        quotations = self._db.scalars(stmt).all()
        return [self._serialize_quotation(quotation) for quotation in quotations]

    def create_quotation(self, payload: QuotationPayload, current_user_id: str) -> QuotationView:
        if not payload.get('items') and not payload.get('groups'):
            raise EmptyQuotationError('Debes agregar al menos un item o grupo')

        client = self._db.get(Client, payload['clientId'])
        if not client:
            raise ClientNotFoundError('Cliente no encontrado')

        if payload.get('projectId') and not self._db.get(Project, payload['projectId']):
            raise ProjectNotFoundError('Proyecto no encontrado')

        parsed_items, parsed_groups, subtotal, discount, tax_value, total = self._calculate_totals(payload)

        quotation = Quotation(
            id=str(uuid4()),
            quotation_number=self._generate_quotation_number(),
            title=payload['title'],
            description=payload.get('description'),
            client_id=payload['clientId'],
            project_id=payload.get('projectId'),
            created_by=current_user_id,
            status=payload['status'],
            valid_until=self._parse_date(payload['validUntil']),
            subtotal=subtotal,
            tax=tax_value,
            discount=discount,
            total=total,
            notes=payload.get('notes'),
            terms=payload.get('terms'),
        )
        self._db.add(quotation)
        self._db.flush()

        for item in parsed_items:
            self._db.add(
                QuotationItem(
                    id=str(uuid4()),
                    quotation_id=quotation.id,
                    inventory_item_id=item['inventoryItemId'],
                    description=item['description'],
                    quantity=item['quantity'],
                    unit_price=item['unitPrice'],
                    total=item['total'],
                    order=item['order'],
                )
            )

        for group in parsed_groups:
            if not self._db.get(ItemGroup, group['groupId']):
                raise ItemGroupNotFoundError('Grupo no encontrado')

            self._db.add(
                QuotationGroup(
                    id=str(uuid4()),
                    quotation_id=quotation.id,
                    group_id=group['groupId'],
                    name=group['name'],
                    description=group['description'],
                    unit_price=group['unitPrice'],
                    quantity=group['quantity'],
                    total=group['total'],
                    order=group['order'],
                )
            )

        self._db.flush()

        quotation = self._db.scalar(
            select(Quotation)
            .where(Quotation.id == quotation.id)
            .options(
                selectinload(Quotation.client),
                selectinload(Quotation.project),
                selectinload(Quotation.created_by_user),
                selectinload(Quotation.items).selectinload(QuotationItem.inventory_item),
                selectinload(Quotation.groups).selectinload(QuotationGroup.group),
            )
        )
        return self._serialize_quotation(quotation)

    def get_quotation(self, quotation_id: str, include_deep: bool) -> QuotationView:
        options = [
            selectinload(Quotation.client),
            selectinload(Quotation.project),
            selectinload(Quotation.created_by_user),
            selectinload(Quotation.items)
            .selectinload(QuotationItem.inventory_item)
            .selectinload(InventoryItem.product)
            .selectinload(Product.category),
            selectinload(Quotation.groups)
            .selectinload(QuotationGroup.group)
            .selectinload(ItemGroup.items)
            .selectinload(ItemGroupItem.inventory_item)
            .selectinload(InventoryItem.product)
            .selectinload(Product.category),
        ]
        quotation = self._db.scalar(select(Quotation).where(Quotation.id == quotation_id).options(*options))

        if not quotation:
            raise QuotationNotFoundError('Cotizacion no encontrada')

        return self._serialize_quotation(quotation, include_deep=include_deep)

    def update_quotation(self, quotation_id: str, payload: QuotationPayload) -> QuotationView:
        quotation = self._db.get(Quotation, quotation_id)
        if not quotation:
            raise QuotationNotFoundError('Cotizacion no encontrada')

        if not payload.get('items') and not payload.get('groups'):
            raise EmptyQuotationError('Debes agregar al menos un item o grupo')

        parsed_items, parsed_groups, subtotal, discount, tax_value, total = self._calculate_totals(payload)

        quotation.title = payload['title']
        quotation.description = payload.get('description')
        quotation.client_id = payload['clientId']
        quotation.project_id = payload.get('projectId')
        quotation.status = payload['status']
        quotation.valid_until = self._parse_date(payload['validUntil'])
        quotation.subtotal = subtotal
        quotation.tax = tax_value
        quotation.discount = discount
        quotation.total = total
        quotation.notes = payload.get('notes')
        quotation.terms = payload.get('terms')

        self._db.execute(delete(QuotationItem).where(QuotationItem.quotation_id == quotation_id))
        self._db.execute(delete(QuotationGroup).where(QuotationGroup.quotation_id == quotation_id))

        for item in parsed_items:
            self._db.add(
                QuotationItem(
                    id=str(uuid4()),
                    quotation_id=quotation_id,
                    inventory_item_id=item['inventoryItemId'],
                    description=item['description'],
                    quantity=item['quantity'],
                    unit_price=item['unitPrice'],
                    total=item['total'],
                    order=item['order'],
                )
            )

        for group in parsed_groups:
            if not self._db.get(ItemGroup, group['groupId']):
                raise ItemGroupNotFoundError('Grupo no encontrado')

            self._db.add(
                QuotationGroup(
                    id=str(uuid4()),
                    quotation_id=quotation_id,
                    group_id=group['groupId'],
                    name=group['name'],
                    description=group['description'],
                    unit_price=group['unitPrice'],
                    quantity=group['quantity'],
                    total=group['total'],
                    order=group['order'],
                )
            )

        self._db.flush()

        quotation = self._db.scalar(
            select(Quotation)
            .where(Quotation.id == quotation_id)
            .options(
                selectinload(Quotation.client),
                selectinload(Quotation.project),
                selectinload(Quotation.created_by_user),
                selectinload(Quotation.items)
                .selectinload(QuotationItem.inventory_item)
                .selectinload(InventoryItem.product)
                .selectinload(Product.category),
                selectinload(Quotation.groups)
                .selectinload(QuotationGroup.group)
                .selectinload(ItemGroup.items)
                .selectinload(ItemGroupItem.inventory_item)
                .selectinload(InventoryItem.product)
                .selectinload(Product.category),
            )
        )

        return self._serialize_quotation(quotation, include_deep=True)

    def delete_quotation(self, quotation_id: str) -> QuotationMutationResult:
        quotation = self._db.get(Quotation, quotation_id)
        if not quotation:
            raise QuotationNotFoundError('Cotizacion no encontrada')

        self._db.delete(quotation)
        self._db.flush()
        return {'success': True}
