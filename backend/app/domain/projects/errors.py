"""Errores de negocio del dominio `projects`."""

class ProjectNotFoundError(Exception):
    pass


class ClientNotFoundError(Exception):
    pass


class AssignedUserNotFoundError(Exception):
    pass


class ProjectPersistenceError(Exception):
    pass


class InvalidDateFormatError(Exception):
    pass


class InvalidProjectFiltersError(Exception):
    pass


class InvalidProjectPayloadError(Exception):
    pass
