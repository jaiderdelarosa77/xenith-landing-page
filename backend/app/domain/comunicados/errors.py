"""Errores de negocio del dominio `comunicados`."""

class ComunicadoError(Exception):
    pass


class ComunicadoRecipientsNotFoundError(ComunicadoError):
    pass


class ComunicadoProviderError(ComunicadoError):
    def __init__(self, message: str, details: dict | str | None = None) -> None:
        super().__init__(message)
        self.details = details
