from datetime import UTC, datetime, timedelta

import pytest

from app.application.auth.use_cases import AuthUseCases
from app.domain.auth.entities import RefreshTokenRecord, UserAccount
from app.domain.auth.errors import InvalidRefreshTokenError, RefreshTokenExpiredError, UserInactiveError


class FakeUsers:
    def __init__(self, user: UserAccount | None):
        self.user = user

    def find_by_email(self, email: str) -> UserAccount | None:
        return self.user

    def find_by_id(self, user_id: str) -> UserAccount | None:
        return self.user


class FakeRefreshTokens:
    def __init__(self):
        self.added = []
        self.revoked = []
        self.record: RefreshTokenRecord | None = None

    def add(self, user_id: str, token_hash: str, expires_at: datetime) -> None:
        self.added.append((user_id, token_hash, expires_at))

    def find_active_by_hash(self, token_hash: str) -> RefreshTokenRecord | None:
        return self.record

    def mark_revoked(self, token_id: str) -> None:
        self.revoked.append(token_id)


class FakePasswords:
    def verify(self, password: str, password_hash: str) -> bool:
        return password == 'ok' and password_hash == 'hashed'

    def hash(self, password: str) -> str:
        return f'h::{password}'


class FakeTokens:
    def create_access(self, user_id: str) -> str:
        return f'acc::{user_id}'

    def create_refresh(self, user_id: str) -> str:
        return f'ref::{user_id}'

    def decode_refresh(self, token: str) -> dict:
        return {'sub': 'u-1'}


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def _build(user: UserAccount | None):
    refresh = FakeRefreshTokens()
    uow = FakeUow()
    uc = AuthUseCases(
        users=FakeUsers(user),
        refresh_tokens=refresh,
        passwords=FakePasswords(),
        tokens=FakeTokens(),
        uow=uow,
        refresh_token_expire_days=7,
    )
    return uc, refresh, uow


def test_authenticate_user_inactive_raises() -> None:
    user = UserAccount('u-1', 'a@b.c', None, None, 'USER', 'hashed', False)
    uc, _, _ = _build(user)

    with pytest.raises(UserInactiveError):
        uc.authenticate_user('A@B.C', 'ok')


def test_issue_token_pair_stores_refresh_and_commits() -> None:
    user = UserAccount('u-1', 'a@b.c', None, None, 'USER', 'hashed', True)
    uc, refresh, uow = _build(user)

    access, refresh_token = uc.issue_token_pair('u-1')

    assert access == 'acc::u-1'
    assert refresh_token == 'ref::u-1'
    assert len(refresh.added) == 1
    assert uow.commits == 1


def test_rotate_refresh_invalid_raises() -> None:
    user = UserAccount('u-1', 'a@b.c', None, None, 'USER', 'hashed', True)
    uc, _, _ = _build(user)

    with pytest.raises(InvalidRefreshTokenError):
        uc.rotate_refresh_token('raw')


def test_rotate_refresh_expired_revokes_and_raises() -> None:
    user = UserAccount('u-1', 'a@b.c', None, None, 'USER', 'hashed', True)
    uc, refresh, uow = _build(user)
    refresh.record = RefreshTokenRecord(
        id='rt-1',
        user_id='u-1',
        token_hash='hash',
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
        revoked=False,
    )

    with pytest.raises(RefreshTokenExpiredError):
        uc.rotate_refresh_token('raw')

    assert refresh.revoked == ['rt-1']
    assert uow.commits == 1
