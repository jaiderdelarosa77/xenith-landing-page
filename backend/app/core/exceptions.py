"""Utilidades core del backend (`exceptions`)."""

from fastapi import HTTPException, status


def api_error(code: str, message: str, status_code: int, details: dict | list | None = None) -> HTTPException:
    payload = {
        'error': {
            'code': code,
            'message': message,
            'details': details,
        }
    }
    return HTTPException(status_code=status_code, detail=payload)


def unauthorized(message: str = 'No autorizado') -> HTTPException:
    return api_error('UNAUTHORIZED', message, status.HTTP_401_UNAUTHORIZED)


def forbidden(message: str = 'Acceso denegado') -> HTTPException:
    return api_error('FORBIDDEN', message, status.HTTP_403_FORBIDDEN)


def not_found(message: str = 'Recurso no encontrado') -> HTTPException:
    return api_error('NOT_FOUND', message, status.HTTP_404_NOT_FOUND)


def bad_request(message: str = 'Solicitud invalida', details: dict | list | None = None) -> HTTPException:
    return api_error('BAD_REQUEST', message, status.HTTP_400_BAD_REQUEST, details)


def too_many_requests(message: str = 'Demasiados intentos, intenta mas tarde') -> HTTPException:
    return api_error('RATE_LIMITED', message, status.HTTP_429_TOO_MANY_REQUESTS)
