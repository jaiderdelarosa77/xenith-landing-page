"""Entidades y estructuras de negocio del dominio `clients`."""

from dataclasses import dataclass


@dataclass(slots=True)
class ClientFilters:
    search: str
