from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aioboto3

from src.storage.config import storage_settings
from src.storage.exceptions import StorageNotConfigured

# One Session is reused process-wide; clients are cheap, short-lived context managers
# created per operation (the standard aioboto3 pattern).
_session = aioboto3.Session()


@asynccontextmanager
async def get_s3_client() -> AsyncIterator:
    """Yield a configured async S3 client. Use as `async with get_s3_client() as s3:`.

    Raises StorageNotConfigured if S3 env vars are unset, so callers surface a clean
    503 instead of an opaque credentials error from botocore.
    """
    if not storage_settings.is_configured:
        raise StorageNotConfigured()
    async with _session.client(
        "s3",
        region_name=storage_settings.REGION,
        endpoint_url=storage_settings.ENDPOINT_URL,
        aws_access_key_id=storage_settings.ACCESS_KEY_ID,
        aws_secret_access_key=storage_settings.SECRET_ACCESS_KEY,
        use_ssl=storage_settings.USE_SSL,
    ) as client:
        yield client
