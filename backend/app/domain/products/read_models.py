"""Modelos tipados de lectura para `products` (salidas/consultas)."""

from typing import TypedDict


class ProductDeleteResult(TypedDict):
    success: bool
