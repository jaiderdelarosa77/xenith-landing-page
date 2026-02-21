import pytest

from app.application.profile.use_cases import ProfileUseCases
from app.domain.profile.errors import InvalidCurrentPasswordError


class FakeRepo:
    def __init__(self):
        self.change_ok = True

    def get_profile(self, user_id: str):
        return {'id': user_id}

    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        return self.change_ok


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_change_password_commits_when_valid() -> None:
    uow = FakeUow()
    uc = ProfileUseCases(FakeRepo(), uow)

    uc.change_password('u1', 'old', 'new')

    assert uow.commits == 1


def test_change_password_raises_when_current_invalid() -> None:
    repo = FakeRepo()
    repo.change_ok = False
    uow = FakeUow()
    uc = ProfileUseCases(repo, uow)

    with pytest.raises(InvalidCurrentPasswordError):
        uc.change_password('u1', 'wrong', 'new')

    assert uow.rollbacks == 1
