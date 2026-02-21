"""Dependencias reutilizables de FastAPI (auth, permisos y utilidades HTTP)."""

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.exceptions import forbidden, unauthorized
from app.db.session import get_db
from app.composition.access_control import (
    AccessUser,
    ForbiddenError,
    InvalidTokenError,
    NotAuthenticatedError,
    UserInactiveOrMissingError,
    get_current_user as get_current_user_composed,
    require_admin as require_admin_composed,
    require_module_edit as require_module_edit_composed,
    require_module_view as require_module_view_composed,
)
from app.core.config import settings


def get_current_user(request: Request, db: Session = Depends(get_db)) -> AccessUser:
    token = request.cookies.get(settings.access_cookie_name)
    try:
        return get_current_user_composed(db, token)
    except NotAuthenticatedError as exc:
        raise unauthorized(str(exc))
    except InvalidTokenError as exc:
        raise unauthorized(str(exc))
    except UserInactiveOrMissingError as exc:
        raise unauthorized(str(exc))


def require_admin(current_user: AccessUser = Depends(get_current_user), db: Session = Depends(get_db)) -> AccessUser:
    try:
        return require_admin_composed(db, current_user)
    except ForbiddenError:
        raise forbidden()


def require_module_view(module: str):
    def dependency(current_user: AccessUser = Depends(get_current_user), db: Session = Depends(get_db)) -> AccessUser:
        try:
            return require_module_view_composed(db, current_user, module)
        except ForbiddenError as exc:
            raise forbidden(str(exc))

    return dependency


def require_module_edit(module: str):
    def dependency(current_user: AccessUser = Depends(get_current_user), db: Session = Depends(get_db)) -> AccessUser:
        try:
            return require_module_edit_composed(db, current_user, module)
        except ForbiddenError as exc:
            raise forbidden(str(exc))

    return dependency
