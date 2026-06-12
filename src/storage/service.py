"""Reusable object-storage operations, backed by S3 (or any S3-compatible store).

Low-level primitives — upload_bytes / delete / presigned_url / public_url — work on
raw keys and bytes and are domain-agnostic. The image helpers — upload_image /
replace_image — add content-type and size validation on top for the common avatar case.
Any domain can persist the returned `key` and resolve a URL from it later.
"""

import functools
import uuid
from contextlib import suppress

import botocore.session
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import UploadFile

from src.storage.client import get_s3_client
from src.storage.config import storage_settings
from src.storage.constants import (
    ALLOWED_IMAGE_CONTENT_TYPES,
    IMAGE_CONTENT_TYPE_EXTENSIONS,
    MAX_IMAGE_BYTES,
)
from src.storage.exceptions import FileTooLarge, StorageError, UnsupportedFileType
from src.storage.schemas import StoredObject


def build_key(prefix: str, extension: str) -> str:
    """A collision-free object key: `<prefix>/<random-hex>.<ext>`."""
    return f"{prefix.strip('/')}/{uuid.uuid4().hex}.{extension.lstrip('.')}"


def public_url(key: str | None) -> str | None:
    """Resolve a stored key to a public URL. None in → None out.

    Prefers PUBLIC_BASE_URL (CDN / public origin); otherwise builds a virtual-hosted-style
    URL from the endpoint or AWS region. For private buckets use presigned_url instead.
    """
    if not key:
        return None
    if storage_settings.PUBLIC_BASE_URL:
        return f"{storage_settings.PUBLIC_BASE_URL.rstrip('/')}/{key}"
    if storage_settings.ENDPOINT_URL:
        return f"{storage_settings.ENDPOINT_URL.rstrip('/')}/{storage_settings.BUCKET}/{key}"
    return f"https://{storage_settings.BUCKET}.s3.{storage_settings.REGION}.amazonaws.com/{key}"


async def upload_bytes(data: bytes, *, key: str, content_type: str) -> StoredObject:
    """Put raw bytes at `key`. Overwrites any existing object at that key."""
    try:
        async with get_s3_client() as s3:
            await s3.put_object(
                Bucket=storage_settings.BUCKET,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
    except (BotoCoreError, ClientError) as exc:
        raise StorageError() from exc
    return StoredObject(key=key, url=public_url(key))


async def delete(key: str) -> None:
    """Delete an object. S3 delete is idempotent — deleting a missing key is not an error."""
    try:
        async with get_s3_client() as s3:
            await s3.delete_object(Bucket=storage_settings.BUCKET, Key=key)
    except (BotoCoreError, ClientError) as exc:
        raise StorageError() from exc


@functools.lru_cache(maxsize=1)
def _presign_client():
    """A long-lived sync botocore client used solely to sign URLs.

    Presigning is local HMAC signing with no network I/O, so it needs neither aioboto3
    nor async. Cached because client construction is comparatively expensive.
    """
    return botocore.session.get_session().create_client(
        "s3",
        region_name=storage_settings.REGION,
        endpoint_url=storage_settings.ENDPOINT_URL,
        aws_access_key_id=storage_settings.ACCESS_KEY_ID,
        aws_secret_access_key=storage_settings.SECRET_ACCESS_KEY,
        use_ssl=storage_settings.USE_SSL,
        config=Config(signature_version="s3v4"),
    )


def presigned_url(key: str | None, *, expires_in: int | None = None) -> str | None:
    """A time-limited URL to GET a (possibly private) object. None in → None out.

    Synchronous on purpose: signing makes no network call, so this is safe to call
    straight from request handlers and from the AdminRead.profile_image_url property
    (an async property would hand Pydantic an un-awaited coroutine). Returns None when
    storage is unconfigured, so read paths degrade gracefully instead of erroring.
    """
    if not key or not storage_settings.is_configured:
        return None
    return _presign_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": storage_settings.BUCKET, "Key": key},
        ExpiresIn=expires_in or storage_settings.PRESIGN_EXPIRY_SECONDS,
    )


async def upload_image(file: UploadFile, *, prefix: str) -> StoredObject:
    """Validate an uploaded image (type + size) and store it under `prefix`."""
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise UnsupportedFileType()

    data = await file.read()
    if len(data) > MAX_IMAGE_BYTES:
        raise FileTooLarge()

    key = build_key(prefix, IMAGE_CONTENT_TYPE_EXTENSIONS[content_type])
    return await upload_bytes(data, key=key, content_type=content_type)


async def replace_image(
    old_key: str | None, file: UploadFile, *, prefix: str
) -> StoredObject:
    """Upload the new image first, then best-effort delete the old one.

    The new object is committed before cleanup, so a failed delete can't lose the upload;
    a stale object is preferable to a broken reference.
    """
    stored = await upload_image(file, prefix=prefix)
    if old_key and old_key != stored.key:
        # orphaned object on failure is fine; sweep later rather than fail the request
        with suppress(StorageError):
            await delete(old_key)
    return stored
