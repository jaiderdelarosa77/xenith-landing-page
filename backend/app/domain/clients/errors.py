"""Errores de negocio del dominio `clients`."""

class ClientNotFoundError(Exception):
    pass


class ClientPersistenceError(Exception):
    pass


class ClientHasRelationsError(Exception):
    pass
