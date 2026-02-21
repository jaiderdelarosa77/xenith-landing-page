"""Adaptador mínimo de Unit of Work sobre una sesión de SQLAlchemy.

Idea clave para arquitectura hexagonal:
- El dominio no conoce SQLAlchemy.
- El caso de uso solo llama a `commit()` / `rollback()` vía un puerto.
- Esta clase traduce esas llamadas al ORM real.
"""

from sqlalchemy.orm import Session


class SqlAlchemyUnitOfWork:
    """Implementación concreta del puerto `UnitOfWork` usando `Session`."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def commit(self) -> None:
        """Confirma la transacción actual."""
        self._db.commit()

    def rollback(self) -> None:
        """Revierte la transacción actual cuando ocurre un error."""
        self._db.rollback()
