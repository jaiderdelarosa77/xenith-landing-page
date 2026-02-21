"""Servicio/proveedor concreto de infraestructura para `auth`."""

from app.core.security import create_access_token, create_refresh_token, decode_refresh_token, hash_password, verify_password
from app.domain.auth.read_models import TokenClaims


class SecurityAdapter:
    def verify(self, password: str, password_hash: str) -> bool:
        return verify_password(password, password_hash)

    def hash(self, password: str) -> str:
        return hash_password(password)

    def create_access(self, user_id: str) -> str:
        return create_access_token(user_id)

    def create_refresh(self, user_id: str) -> str:
        return create_refresh_token(user_id)

    def decode_refresh(self, token: str) -> TokenClaims:
        return decode_refresh_token(token)
