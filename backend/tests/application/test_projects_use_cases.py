import pytest

from app.application.projects.use_cases import ProjectsUseCases
from app.domain.projects.entities import ProjectFilters, ProjectInput, ProjectTaskInput
from app.domain.projects.errors import (
    AssignedUserNotFoundError,
    ClientNotFoundError,
    InvalidProjectFiltersError,
    InvalidProjectPayloadError,
)


class FakeProjectsRepo:
    def __init__(self):
        self.has_client = True
        self.has_user = True

    def list_projects(self, filters):
        return [{'id': 'pr1', 'filters': filters}]

    def create_project(self, payload):
        return {'id': 'pr2', 'title': payload.title}

    def get_project(self, project_id):
        return {'id': project_id}

    def update_project(self, project_id, payload):
        return {'id': project_id, 'title': payload.title}

    def delete_project(self, project_id):
        return {'success': True, 'id': project_id}

    def client_exists(self, client_id: str) -> bool:
        return self.has_client

    def assigned_user_exists(self, user_id: str) -> bool:
        return self.has_user


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def _build():
    uow = FakeUow()
    repo = FakeProjectsRepo()
    uc = ProjectsUseCases(repo, uow)
    return uc, uow, repo


def _payload() -> ProjectInput:
    return ProjectInput(
        title='Proyecto Alpha',
        description='Descripcion valida de proyecto',
        client_id='c1',
        assigned_to='u1',
        status='ACTIVE',
        priority='HIGH',
        start_date=None,
        end_date=None,
        budget=None,
        tags=[],
        notes=None,
        tasks=[
            ProjectTaskInput(
                title='Planificar',
                description=None,
                assigned_to='u1',
                due_date=None,
                priority='MEDIUM',
            )
        ],
    )


def test_list_projects_rejects_too_long_search() -> None:
    uc, _, _ = _build()
    filters = ProjectFilters(search='x' * 201, status_filter='', priority='', client_id='', assigned_to='')

    with pytest.raises(InvalidProjectFiltersError):
        uc.list_projects(filters)


def test_create_project_requires_title() -> None:
    uc, _, _ = _build()
    payload = _payload()
    payload.title = '   '

    with pytest.raises(InvalidProjectPayloadError):
        uc.create_project(payload)


def test_get_project_requires_id() -> None:
    uc, _, _ = _build()

    with pytest.raises(InvalidProjectPayloadError):
        uc.get_project('')


def test_update_project_delegates_with_valid_payload() -> None:
    uc, uow, _ = _build()

    result = uc.update_project('pr1', _payload())

    assert result['id'] == 'pr1'
    assert uow.commits == 1


def test_create_project_rejects_task_without_title() -> None:
    uc, _, _ = _build()
    payload = _payload()
    payload.tasks[0].title = ' '

    with pytest.raises(InvalidProjectPayloadError):
        uc.create_project(payload)


def test_create_project_commits_on_success() -> None:
    uc, uow, _ = _build()

    uc.create_project(_payload())

    assert uow.commits == 1
    assert uow.rollbacks == 0


def test_create_project_raises_when_client_not_found() -> None:
    uc, _, repo = _build()
    repo.has_client = False

    with pytest.raises(ClientNotFoundError):
        uc.create_project(_payload())


def test_update_project_raises_when_assigned_user_not_found() -> None:
    uc, _, repo = _build()
    repo.has_user = False

    with pytest.raises(AssignedUserNotFoundError):
        uc.update_project('pr1', _payload())
