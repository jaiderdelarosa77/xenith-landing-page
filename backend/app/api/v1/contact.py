"""Endpoints HTTP para `contact`.

Traduce request/response entre FastAPI y la capa de composición.
"""

import logging

from fastapi import APIRouter

from app.schemas.contact import ContactRequest

router = APIRouter(prefix='/contact', tags=['contact'])
logger = logging.getLogger(__name__)


@router.post('')
def submit_contact(payload: ContactRequest):
    logger.info(
        'Contact form submission from %s <%s> | subject=%s',
        payload.name,
        payload.email,
        payload.subject,
    )
    return {
        'success': True,
        'message': 'Mensaje enviado correctamente',
    }
