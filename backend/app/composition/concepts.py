"""Composition root de `concepts`: conecta casos de uso con adaptadores concretos."""

from app.application.concepts.use_cases import ConceptsUseCases
from app.domain.concepts.entities import ConceptFilters
from app.domain.concepts.errors import ConceptNotFoundError, ConceptSupplierNotFoundError
from app.infrastructure.concepts.sqlalchemy_repository import SqlAlchemyConceptsRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _use_cases(db) -> ConceptsUseCases:
    return ConceptsUseCases(
        repo=SqlAlchemyConceptsRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )


def list_concepts(db, *, search: str, category: str, supplier_id: str, is_active: str) -> list[dict]:
    return _use_cases(db).list_concepts(
        ConceptFilters(
            search=search,
            category=category,
            supplier_id=supplier_id,
            is_active=is_active,
        )
    )


def create_concept(db, *, payload: dict) -> dict:
    return _use_cases(db).create_concept(payload)


def get_concept(db, concept_id: str) -> dict:
    return _use_cases(db).get_concept(concept_id)


def update_concept(db, *, concept_id: str, payload: dict) -> dict:
    return _use_cases(db).update_concept(concept_id, payload)


def delete_concept(db, concept_id: str) -> dict:
    return _use_cases(db).delete_concept(concept_id)


__all__ = [
    'ConceptNotFoundError',
    'ConceptSupplierNotFoundError',
    'create_concept',
    'delete_concept',
    'get_concept',
    'list_concepts',
    'update_concept',
]
