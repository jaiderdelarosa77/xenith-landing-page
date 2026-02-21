"""Errores de negocio del dominio `products`."""

class ProductNotFoundError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


class SupplierNotFoundError(Exception):
    pass


class ProductSupplierRelationNotFoundError(Exception):
    pass


class DuplicateSkuError(Exception):
    pass


class ProductPersistenceError(Exception):
    pass
