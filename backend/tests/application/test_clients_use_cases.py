import pytest

from app.application.clients.use_cases import ClientsUseCases
from app.domain.clients.entities import ClientFilters


class FakeRepo:
    def list_clients(self, filters):
        return [{'id': 'cl1', 'filters': filters}]

    def create_client(self, payload):
        return {'id': 'cl2', **payload}

    def get_client(self, client_id: str):
        return {'id': client_id}

    def update_client(self, client_id: str, payload):
        return {'id': client_id, **payload}

    def delete_client(self, client_id: str):
        return {'success': True, 'id': client_id}


class FailingRepo(FakeRepo):
    def update_client(self, client_id: str, payload):
        raise RuntimeError('db error')


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_update_client_commits() -> None:
    uow = FakeUow()
    uc = ClientsUseCases(FakeRepo(), uow)

    result = uc.update_client('cl1', {'name': 'N'})

    assert result['id'] == 'cl1'
    assert uow.commits == 1


def test_update_client_rolls_back_on_error() -> None:
    uow = FakeUow()
    uc = ClientsUseCases(FailingRepo(), uow)

    with pytest.raises(RuntimeError):
        uc.update_client('cl1', {'name': 'N'})

    assert uow.rollbacks == 1


def test_list_clients_delegates_filters() -> None:
    uc = ClientsUseCases(FakeRepo(), FakeUow())
    result = uc.list_clients(ClientFilters(search='abc'))

    assert result[0]['id'] == 'cl1'
