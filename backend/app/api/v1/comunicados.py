"""Endpoints HTTP para `comunicados`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.exceptions import bad_request
from app.composition.comunicados import (
    ComunicadoProviderError,
    ComunicadoRecipientsNotFoundError,
    send_comunicado,
)
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.schemas.comunicado import ComunicadoRequest

router = APIRouter(prefix='/comunicados', tags=['comunicados'])


@router.post('')
def send_comunicado(
    payload: ComunicadoRequest,
    request: Request,
    current_user: AccessUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        return send_comunicado(
            db,
            subject=payload.subject.strip(),
            body=payload.body.strip(),
            recipient_ids=payload.userIds,
            performed_by=current_user.id,
            performer_email=current_user.email,
            ip_address=request.headers.get('x-forwarded-for', request.client.host if request.client else None),
            user_agent=request.headers.get('user-agent'),
        )
    except ComunicadoRecipientsNotFoundError as exc:
        raise bad_request(str(exc))
    except ComunicadoProviderError as exc:
        raise bad_request(str(exc), details={'provider': exc.details} if exc.details is not None else None)
