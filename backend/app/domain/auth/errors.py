"""Errores de negocio del dominio `auth`."""

class UserInactiveError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


class RefreshTokenExpiredError(Exception):
    pass
