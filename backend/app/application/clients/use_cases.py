"""Casos de uso de `clients`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.clients.entities import ClientFilters
from app.domain.clients.ports import ClientsRepository, UnitOfWork
from app.domain.clients.read_models import ClientMutationResult, ClientPayload, ClientView


class ClientsUseCases:
    def __init__(self, repo: ClientsRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def list_clients(self, filters: ClientFilters) -> list[ClientView]:
        return self._repo.list_clients(filters)

    def create_client(self, payload: ClientPayload) -> ClientView:
        try:
            result = self._repo.create_client(payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def get_client(self, client_id: str) -> ClientView:
        return self._repo.get_client(client_id)

    def update_client(self, client_id: str, payload: ClientPayload) -> ClientView:
        try:
            result = self._repo.update_client(client_id, payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def delete_client(self, client_id: str) -> ClientMutationResult:
        try:
            result = self._repo.delete_client(client_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise
