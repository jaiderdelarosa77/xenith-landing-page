"""Errores de negocio del dominio `tasks`."""

class TaskNotFoundError(Exception):
    pass


class NoTaskChangesError(Exception):
    pass
