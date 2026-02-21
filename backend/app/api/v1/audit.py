"""Endpoints HTTP para `audit`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_module_view
from app.db.session import get_db
from app.domain.access_control.ports import AccessUser
from app.composition.audit_read import list_logs

router = APIRouter(prefix='/audit', tags=['audit'])


@router.get('')
def list_audit_logs(
    search: str = '',
    action: str = '',
    limit: int = 100,
    _: AccessUser = Depends(require_module_view('historial')),
    db: Session = Depends(get_db),
):
    return list_logs(db, search=search, action=action, limit=limit)
