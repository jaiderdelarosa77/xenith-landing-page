import pytest

from app.application.item_groups.use_cases import ItemGroupsUseCases
from app.domain.item_groups.entities import ItemGroupFilters


class FakeRepo:
    def list_groups(self, filters):
        return [{'id': 'g1', 'filters': filters}]

    def create_group(self, payload):
        return {'id': 'g2', **payload}

    def get_group(self, group_id: str):
        return {'id': group_id}

    def update_group(self, group_id: str, payload):
        return {'id': group_id, **payload}

    def delete_group(self, group_id: str):
        return {'success': True, 'id': group_id}

    def add_item(self, group_id: str, payload):
        return {'success': True, 'groupId': group_id, **payload}

    def remove_item(self, group_id: str, item_id: str):
        return {'success': True, 'groupId': group_id, 'itemId': item_id}


class FailingRepo(FakeRepo):
    def add_item(self, group_id: str, payload):
        raise RuntimeError('db error')


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_add_item_commits() -> None:
    uow = FakeUow()
    uc = ItemGroupsUseCases(FakeRepo(), uow)

    result = uc.add_item('g1', {'itemId': 'i1'})

    assert result['success'] is True
    assert uow.commits == 1


def test_add_item_rolls_back_on_error() -> None:
    uow = FakeUow()
    uc = ItemGroupsUseCases(FailingRepo(), uow)

    with pytest.raises(RuntimeError):
        uc.add_item('g1', {'itemId': 'i1'})

    assert uow.rollbacks == 1


def test_list_groups_delegates_filters() -> None:
    uc = ItemGroupsUseCases(FakeRepo(), FakeUow())
    result = uc.list_groups(ItemGroupFilters(search='kit'))

    assert result[0]['id'] == 'g1'
