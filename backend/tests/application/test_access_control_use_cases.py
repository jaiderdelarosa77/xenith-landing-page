from types import SimpleNamespace

import pytest

from app.application.access_control.use_cases import AccessControlUseCases
from app.domain.access_control.errors import ForbiddenError, NotAuthenticatedError, UserInactiveOrMissingError


class FakeRepo:
    def __init__(self):
        self.user = None
        self.view = False
        self.edit = False

    def find_user_by_id(self, user_id: str):
        return self.user

    def can_view_module(self, user_id: str, module: str) -> bool:
        return self.view

    def can_edit_module(self, user_id: str, module: str) -> bool:
        return self.edit


class FakeTokens:
    def decode_access(self, token: str) -> dict:
        return {'sub': 'u-1'}


class FakeUow:
    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None


def _user(email: str, role: str = 'USER', active: bool = True):
    return SimpleNamespace(id='u-1', email=email, role=SimpleNamespace(value=role), is_active=active)


def test_get_current_user_requires_token() -> None:
    uc = AccessControlUseCases(FakeRepo(), FakeTokens(), FakeUow(), 'root@example.com')
    with pytest.raises(NotAuthenticatedError):
        uc.get_current_user(None)


def test_get_current_user_inactive_raises() -> None:
    repo = FakeRepo()
    repo.user = _user('a@b.com', active=False)
    uc = AccessControlUseCases(repo, FakeTokens(), FakeUow(), 'root@example.com')
    with pytest.raises(UserInactiveOrMissingError):
        uc.get_current_user('token')


def test_superadmin_bypasses_module_checks() -> None:
    repo = FakeRepo()
    user = _user('root@example.com', role='USER', active=True)
    uc = AccessControlUseCases(repo, FakeTokens(), FakeUow(), 'root@example.com')

    assert uc.require_module_view(user, 'inventario') is user
    assert uc.require_module_edit(user, 'inventario') is user


def test_require_admin_denies_non_admin() -> None:
    uc = AccessControlUseCases(FakeRepo(), FakeTokens(), FakeUow(), 'root@example.com')
    with pytest.raises(ForbiddenError):
        uc.require_admin(_user('user@example.com', role='USER'))


def test_require_module_view_denies_without_permission() -> None:
    repo = FakeRepo()
    repo.user = _user('user@example.com', role='ADMIN')
    uc = AccessControlUseCases(repo, FakeTokens(), FakeUow(), 'root@example.com')
    with pytest.raises(ForbiddenError):
        uc.require_module_view(repo.user, 'inventario')
