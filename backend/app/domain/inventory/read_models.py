"""Read models del dominio de inventario.

Aquí se define la forma de los datos que la aplicación devuelve/consume al leer.
Se usan `TypedDict` para tipar diccionarios sin acoplar el dominio al ORM.
"""

from typing import NotRequired, TypedDict


class InventoryUserView(TypedDict):
    name: str
    email: str
    id: NotRequired[str]


class InventoryCategoryView(TypedDict):
    id: str
    name: str
    color: str | None


class InventoryProductView(TypedDict):
    id: str
    sku: str
    name: str
    brand: str | None
    model: str | None
    imageUrl: str | None
    unitPrice: float | None
    rentalPrice: float | None
    category: InventoryCategoryView | None


class InventoryContainerView(TypedDict):
    id: str
    assetTag: str | None
    serialNumber: str | None


class InventoryRfidTagView(TypedDict):
    id: str
    epc: str
    tid: str | None
    status: str
    lastSeenAt: object | None
    firstSeenAt: object | None


class InventoryCountsView(TypedDict):
    movements: int
    contents: int


class InventoryContentProductView(TypedDict):
    name: str
    sku: str


class InventoryContentView(TypedDict):
    id: str
    serialNumber: str | None
    assetTag: str | None
    status: str
    product: InventoryContentProductView | None


class InventoryMovementItemProductView(TypedDict):
    name: str
    sku: str


class InventoryMovementItemView(TypedDict):
    id: str
    serialNumber: str | None
    assetTag: str | None
    product: InventoryMovementItemProductView | None


class InventoryMovementView(TypedDict):
    id: str
    inventoryItemId: str
    type: str
    fromStatus: str | None
    toStatus: str | None
    fromLocation: str | None
    toLocation: str | None
    reason: str | None
    reference: str | None
    performedBy: str
    createdAt: object
    user: InventoryUserView | None
    inventoryItem: NotRequired[InventoryMovementItemView | None]


class InventoryItemView(TypedDict):
    id: str
    productId: str
    serialNumber: str | None
    assetTag: str | None
    type: str
    status: str
    condition: str | None
    location: str | None
    containerId: str | None
    purchaseDate: object | None
    purchasePrice: float | None
    warrantyExpiry: object | None
    notes: str | None
    createdAt: object
    updatedAt: object
    product: InventoryProductView | None
    container: InventoryContainerView | None
    rfidTag: InventoryRfidTagView | None
    _count: InventoryCountsView
    contents: NotRequired[list[InventoryContentView]]
    movements: NotRequired[list[InventoryMovementView]]


class InventorySummaryCategoryView(TypedDict):
    name: str
    color: str | None
    count: int


class InventorySummaryRecentItemProductView(TypedDict):
    name: str


class InventorySummaryRecentItemView(TypedDict):
    product: InventorySummaryRecentItemProductView | None
    serialNumber: str | None
    assetTag: str | None


class InventorySummaryRecentMovementView(TypedDict):
    id: str
    type: str
    createdAt: object
    inventoryItem: InventorySummaryRecentItemView | None
    user: InventoryUserView | None


class InventorySummaryView(TypedDict):
    total: int
    byStatus: dict[str, int]
    byType: dict[str, int]
    byCategory: list[InventorySummaryCategoryView]
    recentMovements: list[InventorySummaryRecentMovementView]


class InventoryMovementsPageView(TypedDict):
    movements: list[InventoryMovementView]
    total: int
    limit: int
    offset: int


class InventoryMutationResult(TypedDict):
    success: bool


class InventoryShortProductView(TypedDict):
    id: str
    sku: str
    name: str


class InventoryCheckInOutResult(TypedDict):
    id: str
    status: str
    location: str | None
    product: InventoryShortProductView | None
