from app.application.quotations.use_cases import QuotationsUseCases
from app.domain.quotations.entities import QuotationFilters


class FakeRepo:
    def __init__(self):
        self.calls = []

    def list_quotations(self, filters):
        self.calls.append(('list', filters))
        return [{'id': 'q1'}]

    def create_quotation(self, payload, current_user_id):
        self.calls.append(('create', payload, current_user_id))
        return {'id': 'q2'}

    def get_quotation(self, quotation_id, include_deep):
        self.calls.append(('get', quotation_id, include_deep))
        return {'id': quotation_id}

    def update_quotation(self, quotation_id, payload):
        self.calls.append(('update', quotation_id, payload))
        return {'id': quotation_id}

    def delete_quotation(self, quotation_id):
        self.calls.append(('delete', quotation_id))
        return {'success': True}


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def test_quotations_use_cases_delegate_calls() -> None:
    repo = FakeRepo()
    uow = FakeUow()
    uc = QuotationsUseCases(repo, uow)

    filters = QuotationFilters(search='x', status_filter='DRAFT', client_id='c1', project_id='p1')
    assert uc.list_quotations(filters) == [{'id': 'q1'}]
    assert uc.create_quotation({'title': 'T'}, 'u1') == {'id': 'q2'}
    assert uc.get_quotation('q9', include_deep=True) == {'id': 'q9'}
    assert uc.update_quotation('q9', {'title': 'N'}) == {'id': 'q9'}
    assert uc.delete_quotation('q9') == {'success': True}

    assert repo.calls[0][0] == 'list'
    assert repo.calls[2] == ('get', 'q9', True)
    assert uow.commits == 3
    assert uow.rollbacks == 0
