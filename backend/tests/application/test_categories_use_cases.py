import pytest

from app.application.categories.use_cases import CategoriesUseCases
from app.domain.categories.entities import CategoryFilters


class FakeRepo:
    def list_categories(self, filters):
        return [{'id': 'c1', 'filters': filters}]

    def create_category(self, payload):
        return {'id': 'c2', **payload}

    def get_category(self, category_id: str):
        return {'id': category_id}

    def update_category(self, category_id: str, payload):
        return {'id': category_id, **payload}

    def delete_category(self, category_id: str):
        return {'success': True, 'id': category_id}


class FailingRepo(FakeRepo):
    def create_category(self, payload):
        raise RuntimeError('db error')


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_create_category_commits() -> None:
    uow = FakeUow()
    uc = CategoriesUseCases(FakeRepo(), uow)

    result = uc.create_category({'name': 'A'})

    assert result['id'] == 'c2'
    assert uow.commits == 1


def test_create_category_rolls_back_on_error() -> None:
    uow = FakeUow()
    uc = CategoriesUseCases(FailingRepo(), uow)

    with pytest.raises(RuntimeError):
        uc.create_category({'name': 'A'})

    assert uow.rollbacks == 1


def test_list_categories_delegates_filters() -> None:
    uc = CategoriesUseCases(FakeRepo(), FakeUow())
    result = uc.list_categories(CategoryFilters(search='abc'))

    assert result[0]['id'] == 'c1'
