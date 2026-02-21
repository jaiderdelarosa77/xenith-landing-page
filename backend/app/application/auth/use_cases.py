"""Casos de uso de `auth`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

import hashlib
from datetime import UTC, datetime, timedelta

from app.domain.auth.entities import UserAccount
from app.domain.auth.errors import InvalidRefreshTokenError, RefreshTokenExpiredError, UserInactiveError
from app.domain.auth.ports import PasswordService, RefreshTokenRepository, TokenService, UnitOfWork, UserAccountRepository


class AuthUseCases:
    def __init__(
        self,
        users: UserAccountRepository,
        refresh_tokens: RefreshTokenRepository,
        passwords: PasswordService,
        tokens: TokenService,
        uow: UnitOfWork,
        refresh_token_expire_days: int,
    ) -> None:
        self._users = users
        self._refresh_tokens = refresh_tokens
        self._passwords = passwords
        self._tokens = tokens
        self._uow = uow
        self._refresh_token_expire_days = refresh_token_expire_days

    def authenticate_user(self, email: str, password: str) -> UserAccount | None:
        user = self._users.find_by_email(email.lower())
        if not user or not user.password_hash:
            return None
        if not self._passwords.verify(password, user.password_hash):
            return None
        if not user.is_active:
            raise UserInactiveError('USER_INACTIVE')
        return user

    def get_user_by_id(self, user_id: str) -> UserAccount | None:
        return self._users.find_by_id(user_id)

    def issue_token_pair(self, user_id: str) -> tuple[str, str]:
        access_token = self._tokens.create_access(user_id)
        refresh_token = self._tokens.create_refresh(user_id)
        refresh_hash = self.hash_token(refresh_token)

        try:
            self._refresh_tokens.add(
                user_id=user_id,
                token_hash=refresh_hash,
                expires_at=datetime.now(UTC) + timedelta(days=self._refresh_token_expire_days),
            )
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise

        return access_token, refresh_token

    def rotate_refresh_token(self, raw_refresh_token: str) -> tuple[str, str]:
        payload = self._tokens.decode_refresh(raw_refresh_token)
        user_id = payload['sub']
        refresh_hash = self.hash_token(raw_refresh_token)

        token_record = self._refresh_tokens.find_active_by_hash(refresh_hash)
        if not token_record:
            raise InvalidRefreshTokenError('INVALID_REFRESH')

        if token_record.expires_at < datetime.now(UTC):
            try:
                self._refresh_tokens.mark_revoked(token_record.id)
                self._uow.commit()
            except Exception:
                self._uow.rollback()
                raise
            raise RefreshTokenExpiredError('REFRESH_EXPIRED')

        try:
            self._refresh_tokens.mark_revoked(token_record.id)

            new_access = self._tokens.create_access(user_id)
            new_refresh = self._tokens.create_refresh(user_id)
            self._refresh_tokens.add(
                user_id=user_id,
                token_hash=self.hash_token(new_refresh),
                expires_at=datetime.now(UTC) + timedelta(days=self._refresh_token_expire_days),
            )
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise

        return new_access, new_refresh

    def revoke_refresh_token(self, raw_refresh_token: str | None) -> None:
        if not raw_refresh_token:
            return

        refresh_hash = self.hash_token(raw_refresh_token)
        token_record = self._refresh_tokens.find_active_by_hash(refresh_hash)
        if token_record:
            try:
                self._refresh_tokens.mark_revoked(token_record.id)
                self._uow.commit()
            except Exception:
                self._uow.rollback()
                raise

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
