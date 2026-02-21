"""Entidades y estructuras de negocio del dominio `concepts`."""

from dataclasses import dataclass


@dataclass(slots=True)
class ConceptFilters:
    search: str
    category: str
    supplier_id: str
    is_active: str
