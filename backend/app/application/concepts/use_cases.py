"""Casos de uso de `concepts`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.concepts.entities import ConceptFilters
from app.domain.concepts.ports import ConceptsRepository, UnitOfWork
from app.domain.concepts.read_models import ConceptMutationResult, ConceptPayload, ConceptView


class ConceptsUseCases:
    def __init__(self, repo: ConceptsRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def list_concepts(self, filters: ConceptFilters) -> list[ConceptView]:
        return self._repo.list_concepts(filters)

    def create_concept(self, payload: ConceptPayload) -> ConceptView:
        try:
            result = self._repo.create_concept(payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def get_concept(self, concept_id: str) -> ConceptView:
        return self._repo.get_concept(concept_id)

    def update_concept(self, concept_id: str, payload: ConceptPayload) -> ConceptView:
        try:
            result = self._repo.update_concept(concept_id, payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def delete_concept(self, concept_id: str) -> ConceptMutationResult:
        try:
            result = self._repo.delete_concept(concept_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise
