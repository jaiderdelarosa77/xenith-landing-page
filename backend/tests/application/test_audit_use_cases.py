from app.application.audit.use_cases import AuditUseCases
from app.domain.audit.entities import AuditFilters


class FakeRepo:
    def __init__(self):
        self.last_filters = None

    def list_logs(self, filters):
        self.last_filters = filters
        return [{'id': 'a1'}]


class FakeUow:
    def commit(self):
        pass

    def rollback(self):
        pass


def test_list_logs_clamps_limit_to_min_and_max() -> None:
    repo = FakeRepo()
    uc = AuditUseCases(repo, FakeUow())

    uc.list_logs(AuditFilters(search='', action='', limit=0))
    assert repo.last_filters.limit == 1

    uc.list_logs(AuditFilters(search='', action='', limit=999))
    assert repo.last_filters.limit == 200
