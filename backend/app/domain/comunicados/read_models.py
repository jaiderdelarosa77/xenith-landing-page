"""Modelos tipados de lectura para `comunicados` (salidas/consultas)."""

from typing import TypedDict


class ComunicadoResult(TypedDict):
    message: str
    id: str | None
