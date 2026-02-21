from datetime import datetime

import pytest

from app.application.users.use_cases import UsersUseCases
from app.domain.users.entities import PermissionInput, RequestContext, UserData
from app.domain.users.errors import SuperadminProtectionError, UserAlreadyExistsError


class FakeUsersRepo:
    def __init__(self):
        self.existing_by_email = False
        self.created_payload = None
        self.updated_payload = None
        self.replaced_permissions = None
        self.user = UserData(
            id='u-1',
            name='U',
            email='user@example.com',
            image=None,
            role='USER',
            position=None,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            permissions=[PermissionInput('inventario', True, False)],
        )

    def list_for_select(self):
        return []

    def list_all(self):
        return []

    def find_by_id(self, user_id: str):
        return self.user

    def exists_by_email(self, email: str, exclude_user_id: str | None = None):
        return self.existing_by_email

    def create_user(self, **kwargs):
        self.created_payload = kwargs
        return 'u-2'

    def update_user(self, user_id: str, updates: dict):
        self.updated_payload = updates

    def replace_permissions(self, user_id: str, permissions):
        self.replaced_permissions = permissions

    def deactivate_user(self, user_id: str):
        pass


class FakeAudit:
    def __init__(self):
        self.entries = []

    def write(self, **kwargs):
        self.entries.append(kwargs)


class FakeHasher:
    def hash(self, password: str) -> str:
        return f'h::{password}'


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def _ctx() -> RequestContext:
    return RequestContext(performed_by='admin-1', ip_address='127.0.0.1', user_agent='pytest')


def _build(repo: FakeUsersRepo):
    audit = FakeAudit()
    uow = FakeUow()
    uc = UsersUseCases(repo, audit, FakeHasher(), uow, 'root@example.com')
    return uc, audit, uow


def test_create_user_normalizes_email_and_writes_audit() -> None:
    repo = FakeUsersRepo()
    uc, audit, uow = _build(repo)

    uc.create_user(
        name='Test',
        email='USER@Example.com',
        password='Secret123',
        role='USER',
        position=None,
        permissions=[],
        ctx=_ctx(),
    )

    assert repo.created_payload['email'] == 'user@example.com'
    assert repo.created_payload['password_hash'] == 'h::Secret123'
    assert audit.entries[0]['action'] == 'USER_CREATED'
    assert uow.commits == 1


def test_create_user_duplicate_email_raises() -> None:
    repo = FakeUsersRepo()
    repo.existing_by_email = True
    uc, _, _ = _build(repo)

    with pytest.raises(UserAlreadyExistsError):
        uc.create_user(
            name='Test',
            email='dup@example.com',
            password='Secret123',
            role='USER',
            position=None,
            permissions=[],
            ctx=_ctx(),
        )


def test_update_user_superadmin_protected() -> None:
    repo = FakeUsersRepo()
    repo.user.email = 'root@example.com'
    uc, _, _ = _build(repo)

    with pytest.raises(SuperadminProtectionError):
        uc.update_user(user_id='u-1', updates={'name': 'x'}, permissions=None, ctx=_ctx())


def test_update_user_permissions_change_sets_audit_action() -> None:
    repo = FakeUsersRepo()
    uc, audit, uow = _build(repo)

    uc.update_user(
        user_id='u-1',
        updates={},
        permissions=[PermissionInput('inventario', True, True)],
        ctx=_ctx(),
    )

    assert repo.replaced_permissions is not None
    assert audit.entries[0]['action'] == 'USER_PERMISSIONS_CHANGED'
    assert 'changes' in audit.entries[0]['metadata']
    assert uow.commits == 1
