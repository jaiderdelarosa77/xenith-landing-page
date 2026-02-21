"""Endpoints HTTP para `auth`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.composition.auth import (
    AuthError,
    InvalidAccessTokenError,
    authenticate_user,
    get_user_from_access_token,
    issue_token_pair,
    revoke_refresh_token,
    rotate_refresh_token,
)
from app.core.config import settings
from app.core.exceptions import bad_request, too_many_requests, unauthorized
from app.core.rate_limit import rate_limiter
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse, AuthUser

router = APIRouter(prefix='/auth', tags=['auth'])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    cookie_kwargs = {
        'httponly': True,
        'secure': settings.cookie_secure,
        'samesite': settings.cookie_samesite,
        'domain': settings.cookie_domain,
        'path': '/',
    }
    response.set_cookie(settings.access_cookie_name, access_token, max_age=settings.access_token_expire_minutes * 60, **cookie_kwargs)
    response.set_cookie(settings.refresh_cookie_name, refresh_token, max_age=settings.refresh_token_expire_days * 24 * 60 * 60, **cookie_kwargs)


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.access_cookie_name, path='/', domain=settings.cookie_domain)
    response.delete_cookie(settings.refresh_cookie_name, path='/', domain=settings.cookie_domain)


@router.post('/login', response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    client_ip = request.headers.get('x-forwarded-for', request.client.host if request.client else 'unknown').split(',')[0].strip()
    rate = rate_limiter.check(f'login:{client_ip}', settings.rate_limit_login_max, settings.rate_limit_login_window_seconds)
    response.headers['X-RateLimit-Limit'] = str(settings.rate_limit_login_max)
    response.headers['X-RateLimit-Remaining'] = str(rate.remaining)
    response.headers['X-RateLimit-Reset'] = str(rate.reset_at)

    if not rate.success:
        raise too_many_requests('Demasiados intentos de inicio de sesion. Intenta de nuevo mas tarde.')

    try:
        user = authenticate_user(db, payload.email, payload.password)
    except AuthError:
        raise bad_request('Tu cuenta ha sido desactivada. Contacta al administrador.')

    if not user:
        raise unauthorized('Credenciales invalidas')

    rate_limiter.reset(f'login:{client_ip}')
    access_token, refresh_token = issue_token_pair(db, user.id)
    _set_auth_cookies(response, access_token, refresh_token)

    return {
        'success': True,
        'user': AuthUser(id=user.id, email=user.email, name=user.name, image=user.image, role=user.role),
    }


@router.post('/refresh', response_model=LoginResponse)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_refresh = request.cookies.get(settings.refresh_cookie_name)
    if not raw_refresh:
        raise unauthorized('Refresh token no encontrado')

    try:
        new_access, new_refresh = rotate_refresh_token(db, raw_refresh)
    except Exception:
        raise unauthorized('Refresh token invalido o expirado')

    _set_auth_cookies(response, new_access, new_refresh)
    try:
        current_user = get_user_from_access_token(db, new_access)
    except InvalidAccessTokenError:
        raise unauthorized('Access token invalido')
    if not current_user:
        raise unauthorized('Usuario no encontrado')
    return {
        'success': True,
        'user': AuthUser(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            image=current_user.image,
            role=current_user.role,
        ),
    }


@router.post('/logout', response_model=LogoutResponse)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    revoke_refresh_token(db, request.cookies.get(settings.refresh_cookie_name))
    _clear_auth_cookies(response)
    return {'success': True, 'message': 'Sesion cerrada exitosamente'}


@router.get('/me', response_model=AuthUser)
def me(current_user: AccessUser = Depends(get_current_user)):
    role = getattr(current_user.role, 'value', current_user.role)
    return AuthUser(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        image=current_user.image,
        role=role,
    )
