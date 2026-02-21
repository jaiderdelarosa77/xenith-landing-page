"""Modelos tipados de lectura para `access_control` (salidas/consultas)."""

from typing import TypedDict


class AccessTokenClaims(TypedDict):
    sub: str
    type: str
    iat: int
    exp: int
