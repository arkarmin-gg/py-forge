import re
from io import BytesIO

import pytest
from src.storage import service
from src.storage.config import storage_settings
from src.storage.exceptions import (
    FileTooLarge,
    StorageNotConfigured,
    UnsupportedFileType,
)
from src.storage.schemas import StoredObject
from starlette.datastructures import Headers, UploadFile


def _upload(data: bytes, content_type: str, name: str = "f") -> UploadFile:
    return UploadFile(
        file=BytesIO(data),
        filename=name,
        headers=Headers({"content-type": content_type}),
    )


def test_build_key_shape() -> None:
    key = service.build_key("admins/abc/avatar", "png")
    assert re.fullmatch(r"admins/abc/avatar/[0-9a-f]{32}\.png", key)


def test_build_key_strips_separators() -> None:
    # leading/trailing slashes on prefix and a dotted ext should normalize cleanly
    key = service.build_key("/p/", ".jpg")
    assert re.fullmatch(r"p/[0-9a-f]{32}\.jpg", key)


def test_public_url_none_for_empty_key() -> None:
    assert service.public_url(None) is None
    assert service.public_url("") is None


def test_public_url_prefers_public_base(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage_settings, "PUBLIC_BASE_URL", "https://cdn.example.com/")
    assert service.public_url("a/b.png") == "https://cdn.example.com/a/b.png"


def test_public_url_uses_endpoint_when_no_public_base(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(storage_settings, "PUBLIC_BASE_URL", None)
    monkeypatch.setattr(storage_settings, "ENDPOINT_URL", "http://localhost:9000")
    monkeypatch.setattr(storage_settings, "BUCKET", "py-forge")
    assert service.public_url("a/b.png") == "http://localhost:9000/py-forge/a/b.png"


def test_public_url_falls_back_to_aws_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage_settings, "PUBLIC_BASE_URL", None)
    monkeypatch.setattr(storage_settings, "ENDPOINT_URL", None)
    monkeypatch.setattr(storage_settings, "BUCKET", "py-forge")
    monkeypatch.setattr(storage_settings, "REGION", "eu-west-1")
    assert (
        service.public_url("a/b.png")
        == "https://py-forge.s3.eu-west-1.amazonaws.com/a/b.png"
    )


async def test_upload_image_rejects_unsupported_type() -> None:
    with pytest.raises(UnsupportedFileType):
        await service.upload_image(_upload(b"x", "text/plain"), prefix="p")


async def test_upload_image_rejects_too_large(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(service, "MAX_IMAGE_BYTES", 4)
    with pytest.raises(FileTooLarge):
        await service.upload_image(_upload(b"toolong", "image/png"), prefix="p")


async def test_upload_image_validates_then_stores(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict = {}

    async def fake_upload_bytes(data: bytes, *, key: str, content_type: str):
        captured.update(data=data, key=key, content_type=content_type)
        return StoredObject(key=key, url=f"https://cdn/{key}")

    monkeypatch.setattr(service, "upload_bytes", fake_upload_bytes)
    result = await service.upload_image(_upload(b"png-bytes", "image/png"), prefix="p")

    assert captured["data"] == b"png-bytes"
    assert captured["content_type"] == "image/png"
    assert re.fullmatch(r"p/[0-9a-f]{32}\.png", result.key)  # ext from content type


async def test_get_s3_client_raises_when_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.storage.client import get_s3_client

    monkeypatch.setattr(storage_settings, "BUCKET", "")
    with pytest.raises(StorageNotConfigured):
        async with get_s3_client():
            pass
