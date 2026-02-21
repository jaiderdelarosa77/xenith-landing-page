"""Entidades y estructuras de negocio del dominio `categories`."""

from dataclasses import dataclass


@dataclass(slots=True)
class CategoryFilters:
    search: str
