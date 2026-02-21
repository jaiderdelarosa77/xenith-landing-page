"""Módulo de infraestructura `access_control`."""

from app.core.security import TokenPayloadError, decode_access_token
from app.domain.access_control.errors import InvalidTokenError
from app.domain.access_control.read_models import AccessTokenClaims


class SecurityTokenDecoder:
    def decode_access(self, token: str) -> AccessTokenClaims:
        try:
            return decode_access_token(token)
        except TokenPayloadError:
            raise InvalidTokenError('Token invalido') from None
