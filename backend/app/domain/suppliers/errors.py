"""Errores de negocio del dominio `suppliers`."""

class SupplierNotFoundError(Exception):
    pass


class SupplierHasProductsError(Exception):
    pass
