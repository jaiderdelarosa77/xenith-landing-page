"""Entidades y estructuras de negocio del dominio `products`."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class CategoryData:
    id: str
    name: str
    color: str | None


@dataclass(slots=True)
class InventoryItemLite:
    id: str
    serial_number: str | None
    asset_tag: str | None
    status: str
    condition: str | None
    location: str | None


@dataclass(slots=True)
class SupplierLite:
    id: str
    name: str
    email: str | None
    phone: str | None


@dataclass(slots=True)
class ProductSupplierData:
    product_id: str
    supplier_id: str
    supplier_sku: str | None
    cost: float | None
    is_preferred: bool
    supplier: SupplierLite


@dataclass(slots=True)
class ProductData:
    id: str
    sku: str
    name: str
    description: str | None
    category_id: str
    brand: str | None
    model: str | None
    status: str
    unit_price: float | None
    rental_price: float | None
    image_url: str | None
    notes: str | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime
    category: CategoryData | None
    inventory_count: int
    suppliers: list[ProductSupplierData]
    inventory_items: list[InventoryItemLite]


@dataclass(slots=True)
class ProductWriteInput:
    sku: str
    name: str
    description: str | None
    category_id: str
    brand: str | None
    model: str | None
    status: str
    unit_price: float | None
    rental_price: float | None
    image_url: str | None
    notes: str | None


@dataclass(slots=True)
class ProductListFilters:
    search: str
    category: str
    status_filter: str
    include_deleted: bool


@dataclass(slots=True)
class ProductSupplierInput:
    supplier_id: str
    supplier_sku: str | None
    cost: float | None
    is_preferred: bool
