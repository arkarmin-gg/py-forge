import jwt
import pytest
from src.modules.auth import security


def test_password_hash_roundtrip() -> None:
    password = "correct horse battery staple"
    hashed = security.hash_password(password)
    assert hashed != password
    assert security.verify_password(password, hashed)
    assert not security.verify_password("wrong password", hashed)


def test_access_token_roundtrip() -> None:
    token = security.create_access_token("admin-123")
    payload = security.decode_access_token(token)
    assert payload["sub"] == "admin-123"
    assert payload["type"] == "access"


def test_decode_rejects_tampered_token() -> None:
    token = security.create_access_token("admin-123")
    with pytest.raises(jwt.InvalidTokenError):
        security.decode_access_token(token + "garbage")


def test_decode_rejects_wrong_secret() -> None:
    token = jwt.encode({"sub": "x", "type": "access"}, "a-different-secret", algorithm="HS256")
    with pytest.raises(jwt.InvalidTokenError):
        security.decode_access_token(token)


def test_refresh_token_is_opaque_and_hash_is_stable() -> None:
    raw = security.generate_refresh_token()
    assert security.hash_refresh_token(raw) == security.hash_refresh_token(raw)
    assert raw not in security.hash_refresh_token(raw)
