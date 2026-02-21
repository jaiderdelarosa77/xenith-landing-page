"""Puertos (interfaces) del dominio `clients` para desacoplar infraestructura."""

from typing import Protocol

from app.domain.clients.entities import ClientFilters
from app.domain.clients.read_models import ClientMutationResult, ClientPayload, ClientView


class ClientsRepository(Protocol):
    def list_clients(self, filters: ClientFilters) -> list[ClientView]: ...

    def create_client(self, payload: ClientPayload) -> ClientView: ...

    def get_client(self, client_id: str) -> ClientView: ...

    def update_client(self, client_id: str, payload: ClientPayload) -> ClientView: ...

    def delete_client(self, client_id: str) -> ClientMutationResult: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
