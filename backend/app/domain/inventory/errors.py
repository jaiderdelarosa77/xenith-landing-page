"""Errores de negocio del dominio `inventory`."""

class InventoryItemNotFoundError(Exception):
    pass


class ProductNotFoundOrInactiveError(Exception):
    pass


class InvalidDateFormatError(Exception):
    pass


class DuplicateSerialError(Exception):
    pass


class DuplicateAssetTagError(Exception):
    pass


class InventoryPersistenceError(Exception):
    pass


class ContainerHasItemsError(Exception):
    pass


class AlreadyCheckedInError(Exception):
    pass


class AlreadyCheckedOutError(Exception):
    pass


class LostItemCheckOutError(Exception):
    pass


class InvalidInventoryFiltersError(Exception):
    pass


class InvalidInventoryPayloadError(Exception):
    pass
