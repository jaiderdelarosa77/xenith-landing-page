"""Errores de negocio del dominio `item_groups`."""

class ItemGroupNotFoundError(Exception):
    pass


class InventoryItemNotFoundError(Exception):
    pass


class ItemAlreadyInGroupError(Exception):
    pass


class ItemNotInGroupError(Exception):
    pass
