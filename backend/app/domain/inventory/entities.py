"""Entidades de entrada/filtros del dominio de inventario.

Estas clases NO dependen de FastAPI ni SQLAlchemy: representan datos de negocio.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class InventoryListFilters:
    """Filtros permitidos para listar items de inventario."""

    search: str
    status_filter: str
    type_filter: str
    product_id: str
    container_id: str


@dataclass(slots=True)
class MovementListFilters:
    """Filtros de paginación/búsqueda para movimientos de inventario."""

    type_filter: str
    inventory_item_id: str
    limit: int
    offset: int


@dataclass(slots=True)
class InventoryItemInput:
    """Payload de negocio para crear/editar un item."""

    product_id: str
    serial_number: str | None
    asset_tag: str | None
    item_type: str
    status: str
    condition: str | None
    location: str | None
    container_id: str | None
    purchase_date: str | None
    purchase_price: float | None
    warranty_expiry: str | None
    notes: str | None


@dataclass(slots=True)
class CheckInOutInput:
    """Datos opcionales de contexto para check-in/check-out."""

    location: str | None
    reason: str | None
    reference: str | None
