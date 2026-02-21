"""Modelos tipados de lectura para `profile` (salidas/consultas)."""

from typing import TypedDict


class ProfileView(TypedDict, total=False):
    id: str
    name: str
    email: str
    role: str
    image: str | None
    position: str | None
