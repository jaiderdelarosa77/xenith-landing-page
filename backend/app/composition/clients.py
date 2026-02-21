"""Composition root de `clients`: conecta casos de uso con adaptadores concretos."""

from app.application.clients.use_cases import ClientsUseCases
from app.domain.clients.entities import ClientFilters
from app.domain.clients.errors import ClientHasRelationsError, ClientNotFoundError, ClientPersistenceError
from app.infrastructure.clients.sqlalchemy_repository import SqlAlchemyClientsRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _use_cases(db) -> ClientsUseCases:
    return ClientsUseCases(
        repo=SqlAlchemyClientsRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )


def list_clients(db, *, search: str) -> list[dict]:
    return _use_cases(db).list_clients(ClientFilters(search=search))


def create_client(db, *, payload: dict) -> dict:
    return _use_cases(db).create_client(payload)


def get_client(db, client_id: str) -> dict:
    return _use_cases(db).get_client(client_id)


def update_client(db, *, client_id: str, payload: dict) -> dict:
    return _use_cases(db).update_client(client_id, payload)


def delete_client(db, client_id: str) -> dict:
    return _use_cases(db).delete_client(client_id)


__all__ = [
    'ClientHasRelationsError',
    'ClientNotFoundError',
    'ClientPersistenceError',
    'create_client',
    'delete_client',
    'get_client',
    'list_clients',
    'update_client',
]
