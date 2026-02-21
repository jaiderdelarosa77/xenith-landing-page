"""Errores de negocio del dominio `rfid`."""

class TagNotFoundError(Exception):
    pass


class DuplicateEpcError(Exception):
    pass


class InventoryItemNotFoundError(Exception):
    pass


class InventoryItemAlreadyLinkedError(Exception):
    pass


class TagAlreadyLinkedError(Exception):
    pass


class InvalidTimestampError(Exception):
    pass


class InvalidApiKeyError(Exception):
    pass
