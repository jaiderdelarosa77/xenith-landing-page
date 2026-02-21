"""Entidades y estructuras de negocio del dominio `item_groups`."""

from dataclasses import dataclass


@dataclass(slots=True)
class ItemGroupFilters:
    search: str
