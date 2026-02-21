"""Entidades y estructuras de negocio del dominio `quotations`."""

from dataclasses import dataclass


@dataclass(slots=True)
class QuotationFilters:
    search: str
    status_filter: str
    client_id: str
    project_id: str
