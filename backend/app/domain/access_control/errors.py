"""Errores de negocio del dominio `access_control`."""

class NotAuthenticatedError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class UserInactiveOrMissingError(Exception):
    pass


class ForbiddenError(Exception):
    pass
