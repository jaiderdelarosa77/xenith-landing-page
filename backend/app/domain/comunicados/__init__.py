"""Paquete `comunicados` del backend."""

from app.domain.comunicados.errors import ComunicadoError, ComunicadoProviderError, ComunicadoRecipientsNotFoundError
from app.domain.comunicados.read_models import ComunicadoResult

__all__ = [
    'ComunicadoError',
    'ComunicadoProviderError',
    'ComunicadoRecipientsNotFoundError',
    'ComunicadoResult',
]
