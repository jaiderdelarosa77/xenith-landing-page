"""Puertos (interfaces) del dominio `concepts` para desacoplar infraestructura."""

from typing import Protocol

from app.domain.concepts.entities import ConceptFilters
from app.domain.concepts.read_models import ConceptMutationResult, ConceptPayload, ConceptView


class ConceptsRepository(Protocol):
    def list_concepts(self, filters: ConceptFilters) -> list[ConceptView]: ...

    def create_concept(self, payload: ConceptPayload) -> ConceptView: ...

    def get_concept(self, concept_id: str) -> ConceptView: ...

    def update_concept(self, concept_id: str, payload: ConceptPayload) -> ConceptView: ...

    def delete_concept(self, concept_id: str) -> ConceptMutationResult: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
