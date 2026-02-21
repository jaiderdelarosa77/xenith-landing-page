"""Utilidades core del backend (`security`)."""

from datetime import UTC, datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class TokenPayloadError(Exception):
    pass


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def _create_token(subject: str, expires_delta: timedelta, secret: str, token_type: str) -> str:
    now = datetime.now(UTC)
    payload = {
        'sub': subject,
        'type': token_type,
        'iat': int(now.timestamp()),
        'exp': int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    return _create_token(
        subject,
        timedelta(minutes=settings.access_token_expire_minutes),
        settings.jwt_access_secret,
        'access',
    )


def create_refresh_token(subject: str) -> str:
    return _create_token(
        subject,
        timedelta(days=settings.refresh_token_expire_days),
        settings.jwt_refresh_secret,
        'refresh',
    )


def decode_access_token(token: str) -> dict:
    return _decode_token(token, settings.jwt_access_secret, 'access')


def decode_refresh_token(token: str) -> dict:
    return _decode_token(token, settings.jwt_refresh_secret, 'refresh')


def _decode_token(token: str, secret: str, token_type: str) -> dict:
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise TokenPayloadError('Token invalido') from exc

    if payload.get('type') != token_type:
        raise TokenPayloadError('Tipo de token invalido')

    subject = payload.get('sub')
    if not subject:
        raise TokenPayloadError('Token sin sujeto')

    return payload
