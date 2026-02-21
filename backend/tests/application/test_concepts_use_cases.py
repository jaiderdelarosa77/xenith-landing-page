import pytest

from app.application.concepts.use_cases import ConceptsUseCases
from app.domain.concepts.entities import ConceptFilters


class FakeRepo:
    def list_concepts(self, filters):
        return [{'id': 'co1', 'filters': filters}]

    def create_concept(self, payload):
        return {'id': 'co2', **payload}

    def get_concept(self, concept_id: str):
        return {'id': concept_id}

    def update_concept(self, concept_id: str, payload):
        return {'id': concept_id, **payload}

    def delete_concept(self, concept_id: str):
        return {'success': True, 'id': concept_id}


class FailingRepo(FakeRepo):
    def delete_concept(self, concept_id: str):
        raise RuntimeError('db error')


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_delete_concept_rolls_back_on_error() -> None:
    uow = FakeUow()
    uc = ConceptsUseCases(FailingRepo(), uow)

    with pytest.raises(RuntimeError):
        uc.delete_concept('co1')

    assert uow.rollbacks == 1


def test_create_concept_commits() -> None:
    uow = FakeUow()
    uc = ConceptsUseCases(FakeRepo(), uow)

    result = uc.create_concept({'name': 'X'})

    assert result['id'] == 'co2'
    assert uow.commits == 1


def test_list_concepts_delegates_filters() -> None:
    uc = ConceptsUseCases(FakeRepo(), FakeUow())
    result = uc.list_concepts(ConceptFilters(search='', category='', supplier_id='', is_active=''))

    assert result[0]['id'] == 'co1'
