"""Endpoints HTTP para `profile`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import bad_request
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.schemas.user import ChangePasswordRequest
from app.composition.profile import InvalidCurrentPasswordError, change_password, get_profile

router = APIRouter(prefix='/profile', tags=['profile'])


@router.get('')
def get_profile_route(current_user: AccessUser = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_profile(db, current_user.id)


@router.put('/change-password')
def update_password(
    payload: ChangePasswordRequest,
    current_user: AccessUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        change_password(
            db,
            user_id=current_user.id,
            current_password=payload.currentPassword,
            new_password=payload.newPassword,
        )
    except InvalidCurrentPasswordError as exc:
        raise bad_request(str(exc))

    return {'message': 'Contrasena actualizada exitosamente'}
