"""Errores de negocio del dominio `categories`."""

class CategoryNotFoundError(Exception):
    pass


class CategoryDuplicateNameError(Exception):
    pass


class CategoryHasProductsError(Exception):
    pass
