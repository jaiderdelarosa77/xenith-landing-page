"""Entidades y estructuras de negocio del dominio `suppliers`."""

from dataclasses import dataclass


@dataclass(slots=True)
class SupplierFilters:
    search: str
