"""Adaptador de infraestructura para `concepts` (persistencia concreta)."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, selectinload

from app.domain.concepts.entities import ConceptFilters
from app.domain.concepts.errors import ConceptNotFoundError, ConceptSupplierNotFoundError
from app.models.catalog_inventory import Concept, Supplier


class SqlAlchemyConceptsRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _serialize_concept(concept: Concept) -> dict:
        return {
            'id': concept.id,
            'name': concept.name,
            'description': concept.description,
            'supplierId': concept.supplier_id,
            'unitPrice': float(concept.unit_price) if concept.unit_price is not None else None,
            'category': concept.category,
            'notes': concept.notes,
            'isActive': concept.is_active,
            'createdAt': concept.created_at,
            'updatedAt': concept.updated_at,
            'supplier': {
                'id': concept.supplier.id,
                'name': concept.supplier.name,
                'contactName': concept.supplier.contact_name,
                'email': concept.supplier.email,
                'phone': concept.supplier.phone,
            }
            if concept.supplier
            else None,
        }

    @staticmethod
    def _normalize(payload: dict) -> dict:
        return {
            'name': payload['name'].strip(),
            'description': (payload.get('description') or '').strip() or None,
            'supplier_id': payload.get('supplierId') or None,
            'unit_price': Decimal(str(payload['unitPrice'])) if payload.get('unitPrice') is not None else None,
            'category': (payload.get('category') or '').strip() or None,
            'notes': (payload.get('notes') or '').strip() or None,
            'is_active': payload.get('isActive', True),
        }

    def list_concepts(self, filters: ConceptFilters) -> list[dict]:
        conditions = []
        if filters.search:
            search_like = f'%{filters.search}%'
            conditions.append(or_(Concept.name.ilike(search_like), Concept.description.ilike(search_like), Concept.supplier.has(Supplier.name.ilike(search_like))))
        if filters.category:
            conditions.append(Concept.category == filters.category)
        if filters.supplier_id:
            conditions.append(Concept.supplier_id == filters.supplier_id)
        if filters.is_active == 'true':
            conditions.append(Concept.is_active.is_(True))
        elif filters.is_active == 'false':
            conditions.append(Concept.is_active.is_(False))

        stmt = select(Concept).options(selectinload(Concept.supplier)).order_by(Concept.name.asc())
        if conditions:
            stmt = stmt.where(and_(*conditions))

        concepts = self._db.scalars(stmt).all()
        return [self._serialize_concept(concept) for concept in concepts]

    def create_concept(self, payload: dict) -> dict:
        normalized = self._normalize(payload)
        if normalized['supplier_id'] and not self._db.get(Supplier, normalized['supplier_id']):
            raise ConceptSupplierNotFoundError('Contratista no encontrado')

        concept = Concept(id=str(uuid4()), **normalized)
        self._db.add(concept)
        self._db.flush()

        concept = self._db.scalar(select(Concept).where(Concept.id == concept.id).options(selectinload(Concept.supplier)))
        return self._serialize_concept(concept)

    def get_concept(self, concept_id: str) -> dict:
        concept = self._db.scalar(select(Concept).where(Concept.id == concept_id).options(selectinload(Concept.supplier)))
        if not concept:
            raise ConceptNotFoundError('Concepto no encontrado')
        return self._serialize_concept(concept)

    def update_concept(self, concept_id: str, payload: dict) -> dict:
        concept = self._db.get(Concept, concept_id)
        if not concept:
            raise ConceptNotFoundError('Concepto no encontrado')

        normalized = self._normalize(payload)
        if normalized['supplier_id'] and not self._db.get(Supplier, normalized['supplier_id']):
            raise ConceptSupplierNotFoundError('Contratista no encontrado')

        for field, value in normalized.items():
            setattr(concept, field, value)
        self._db.flush()

        concept = self._db.scalar(select(Concept).where(Concept.id == concept_id).options(selectinload(Concept.supplier)))
        return self._serialize_concept(concept)

    def delete_concept(self, concept_id: str) -> dict:
        concept = self._db.get(Concept, concept_id)
        if not concept:
            raise ConceptNotFoundError('Concepto no encontrado')

        self._db.delete(concept)
        self._db.flush()
        return {'message': 'Concepto eliminado exitosamente'}
