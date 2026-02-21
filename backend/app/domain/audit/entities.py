"""Entidades y estructuras de negocio del dominio `audit`."""

from dataclasses import dataclass


@dataclass(slots=True)
class AuditFilters:
    search: str
    action: str
    limit: int
