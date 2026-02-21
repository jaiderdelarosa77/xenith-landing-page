"""Errores de negocio del dominio `quotations`."""

class QuotationNotFoundError(Exception):
    pass


class ClientNotFoundError(Exception):
    pass


class ProjectNotFoundError(Exception):
    pass


class ItemGroupNotFoundError(Exception):
    pass


class EmptyQuotationError(Exception):
    pass


class InvalidValidUntilError(Exception):
    pass
