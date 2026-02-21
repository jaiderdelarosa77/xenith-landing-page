import pytest

from app.application.tasks.use_cases import TasksUseCases
from app.domain.tasks.entities import TaskFilters
from app.domain.tasks.errors import NoTaskChangesError


class FakeRepo:
    def list_tasks(self, filters):
        return [{'id': 't1', 'filters': filters}]

    def get_task(self, task_id: str):
        return {'id': task_id}

    def update_task(self, task_id: str, payload: dict):
        return {'id': task_id, **payload}


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_update_task_requires_changes() -> None:
    uc = TasksUseCases(FakeRepo(), FakeUow())

    with pytest.raises(NoTaskChangesError):
        uc.update_task('t1', {})


def test_update_task_commits_when_valid() -> None:
    uow = FakeUow()
    uc = TasksUseCases(FakeRepo(), uow)

    result = uc.update_task('t1', {'status': 'DONE'})

    assert result['id'] == 't1'
    assert uow.commits == 1


def test_list_tasks_delegates_filters() -> None:
    uc = TasksUseCases(FakeRepo(), FakeUow())
    result = uc.list_tasks(TaskFilters(search='', status_filter='', priority='', assigned_to='', my_tasks=False, current_user_id='u1'))

    assert result[0]['id'] == 't1'
