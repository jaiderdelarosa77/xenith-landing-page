"""Entidades y estructuras de negocio del dominio `rfid`."""

from dataclasses import dataclass


@dataclass(slots=True)
class TagFilters:
    search: str
    status_filter: str


@dataclass(slots=True)
class DetectionFilters:
    rfid_tag_id: str
    reader_id: str
    direction: str
    limit: int
    offset: int
