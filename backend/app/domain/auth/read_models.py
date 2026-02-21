"""Modelos tipados de lectura para `auth` (salidas/consultas)."""

from typing import TypedDict


class TokenClaims(TypedDict):
    sub: str
    type: str
    iat: int
    exp: int
