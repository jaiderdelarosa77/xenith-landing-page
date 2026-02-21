"""Módulo de infraestructura `storage`."""

from __future__ import annotations

from datetime import datetime
import mimetypes
import os
from urllib.parse import quote

import boto3
from botocore.client import BaseClient
from botocore.config import Config

from app.core.config import settings


def _required(name: str, value: str | None) -> str:
    if value is None or value == '':
        raise RuntimeError(f'R2 no configurado: falta {name}')
    return value


def _clean_prefix(prefix: str) -> str:
    return prefix.strip('/').strip()


def _timestamped_key(filename: str) -> str:
    prefix = _clean_prefix(settings.r2_products_prefix) or 'products'
    safe_name = ''.join(ch.lower() if ch.isalnum() or ch in '._-' else '-' for ch in filename)
    return f'{prefix}/{int(datetime.utcnow().timestamp() * 1000)}-{safe_name}'


def _endpoint_url() -> str:
    if settings.r2_endpoint:
        return settings.r2_endpoint.rstrip('/')
    account_id = _required('R2_ACCOUNT_ID', settings.r2_account_id)
    return f'https://{account_id}.r2.cloudflarestorage.com'


def _public_url() -> str:
    return _required('R2_PUBLIC_URL', settings.r2_public_url).rstrip('/')


def _client() -> BaseClient:
    return boto3.client(
        's3',
        endpoint_url=_endpoint_url(),
        region_name=settings.r2_region,
        aws_access_key_id=_required('R2_ACCESS_KEY_ID', settings.r2_access_key_id),
        aws_secret_access_key=_required('R2_SECRET_ACCESS_KEY', settings.r2_secret_access_key),
        config=Config(signature_version='s3v4'),
    )


def build_product_image_key(filename: str) -> str:
    base = os.path.basename(filename or 'image')
    if '.' not in base:
        guessed_ext = mimetypes.guess_extension('image/jpeg') or '.jpg'
        base = f'{base}{guessed_ext}'
    return _timestamped_key(base)


def build_public_file_url(key: str) -> str:
    return f'{_public_url()}/{quote(key, safe="/")}'


def parse_managed_r2_key_from_url(url: str) -> str | None:
    public = _public_url()
    if not url.startswith(f'{public}/'):
        return None
    key = url[len(public) + 1 :]
    prefix = _clean_prefix(settings.r2_products_prefix) or 'products'
    if not key.startswith(f'{prefix}/'):
        return None
    return key


def upload_bytes_to_r2(*, key: str, body: bytes, content_type: str) -> None:
    bucket = _required('R2_BUCKET_NAME', settings.r2_bucket_name)
    _client().put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType=content_type,
    )


def delete_object_from_r2(key: str) -> None:
    bucket = _required('R2_BUCKET_NAME', settings.r2_bucket_name)
    _client().delete_object(Bucket=bucket, Key=key)
