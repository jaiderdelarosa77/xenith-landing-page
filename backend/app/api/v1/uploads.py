"""Endpoints HTTP para `uploads`.

Traduce request/response entre FastAPI y la capa de composición.
"""

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import require_module_edit
from app.domain.access_control.ports import AccessUser
from app.core.exceptions import bad_request
from app.composition.uploads import (
    ImageTooLargeError,
    InvalidImageTypeError,
    MissingImageUrlError,
    delete_product_image as delete_product_image_composed,
    upload_product_image as upload_product_image_composed,
)

router = APIRouter(prefix='/uploads/products', tags=['uploads'])


@router.post('')
def upload_product_image(
    file: UploadFile = File(...),
    _: AccessUser = Depends(require_module_edit('productos')),
):
    content = file.file.read()
    try:
        return upload_product_image_composed(
            filename=file.filename or 'image',
            content_type=file.content_type,
            content=content,
        )
    except InvalidImageTypeError as exc:
        raise bad_request(str(exc))
    except ImageTooLargeError as exc:
        raise bad_request(str(exc))


@router.delete('')
def delete_product_image(
    payload: dict,
    _: AccessUser = Depends(require_module_edit('productos')),
):
    try:
        return delete_product_image_composed(image_url=str(payload.get('url') or ''))
    except MissingImageUrlError as exc:
        raise bad_request(str(exc))
