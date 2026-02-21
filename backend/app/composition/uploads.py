"""Composition root de `uploads`: conecta casos de uso con adaptadores concretos."""

from app.infrastructure.storage.r2 import (
    build_product_image_key,
    build_public_file_url,
    delete_object_from_r2,
    parse_managed_r2_key_from_url,
    upload_bytes_to_r2,
)

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}


class InvalidImageTypeError(Exception):
    pass


class ImageTooLargeError(Exception):
    pass


class MissingImageUrlError(Exception):
    pass


def upload_product_image(*, filename: str, content_type: str | None, content: bytes) -> dict:
    if content_type not in ALLOWED_MIME_TYPES:
        raise InvalidImageTypeError('Formato no soportado. Usa JPG, PNG o WEBP')

    if len(content) > MAX_FILE_SIZE:
        raise ImageTooLargeError('La imagen no puede ser mayor a 5MB')

    key = build_product_image_key(filename or 'image')
    upload_bytes_to_r2(
        key=key,
        body=content,
        content_type=content_type or 'application/octet-stream',
    )
    return {
        'key': key,
        'url': build_public_file_url(key),
    }


def delete_product_image(*, image_url: str) -> dict:
    normalized_url = image_url.strip()
    if not normalized_url:
        raise MissingImageUrlError('URL de imagen requerida')

    key = parse_managed_r2_key_from_url(normalized_url)
    if not key:
        return {'success': True, 'skipped': True}

    delete_object_from_r2(key)
    return {'success': True}


__all__ = [
    'ImageTooLargeError',
    'InvalidImageTypeError',
    'MissingImageUrlError',
    'delete_product_image',
    'upload_product_image',
]
