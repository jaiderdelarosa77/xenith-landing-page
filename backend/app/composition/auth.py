"""Composition root de `auth`: conecta casos de uso con adaptadores concretos."""

from sqlalchemy.orm import Session

from app.application.auth.use_cases import AuthUseCases
from app.core.security import TokenPayloadError, decode_access_token
from app.core.config import settings
from app.domain.auth.entities import UserAccount
from app.domain.auth.errors import RefreshTokenExpiredError, UserInactiveError
from app.infrastructure.auth.security_service import SecurityAdapter
from app.infrastructure.auth.sqlalchemy_repository import (
    SqlAlchemyAuthRepository,
    SqlAlchemyRefreshTokenRepository,
)
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


class AuthError(Exception):
    pass


class InvalidAccessTokenError(Exception):
    pass


def _build_use_cases(db: Session) -> AuthUseCases:
    return AuthUseCases(
        users=SqlAlchemyAuthRepository(db),
        refresh_tokens=SqlAlchemyRefreshTokenRepository(db),
        passwords=SecurityAdapter(),
        tokens=SecurityAdapter(),
        uow=SqlAlchemyUnitOfWork(db),
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )


def authenticate_user(db: Session, email: str, password: str) -> UserAccount | None:
    try:
        return _build_use_cases(db).authenticate_user(email, password)
    except UserInactiveError:
        raise AuthError('USER_INACTIVE') from None


def issue_token_pair(db: Session, user_id: str) -> tuple[str, str]:
    return _build_use_cases(db).issue_token_pair(user_id)


def rotate_refresh_token(db: Session, raw_refresh_token: str) -> tuple[str, str]:
    try:
        return _build_use_cases(db).rotate_refresh_token(raw_refresh_token)
    except RefreshTokenExpiredError:
        raise AuthError('REFRESH_EXPIRED') from None


def revoke_refresh_token(db: Session, raw_refresh_token: str | None) -> None:
    _build_use_cases(db).revoke_refresh_token(raw_refresh_token)


def get_user_from_access_token(db: Session, access_token: str) -> UserAccount | None:
    try:
        payload = decode_access_token(access_token)
    except TokenPayloadError:
        raise InvalidAccessTokenError('INVALID_ACCESS') from None

    return _build_use_cases(db).get_user_by_id(payload['sub'])
