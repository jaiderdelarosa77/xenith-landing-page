"""Errores de negocio del dominio `users`."""

class UserNotFoundError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class SuperadminProtectionError(Exception):
    pass


class SuperadminRoleAssignmentError(Exception):
    pass
