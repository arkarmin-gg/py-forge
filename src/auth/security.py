import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.auth.config import auth_settings

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    return True


def needs_rehash(password_hash: str) -> bool:
    """True if the hash was made with outdated parameters and should be re-hashed on next login."""
    return _hasher.check_needs_rehash(password_hash)


def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    now = datetime.now(UTC)
    payload: dict = {
        "sub": subject,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=auth_settings.JWT_ACCESS_EXP_MINUTES),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, auth_settings.JWT_SECRET, algorithm=auth_settings.JWT_ALG)


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT. Raises jwt.InvalidTokenError on any failure."""
    return jwt.decode(token, auth_settings.JWT_SECRET, algorithms=[auth_settings.JWT_ALG])


def generate_refresh_token() -> str:
    """A high-entropy opaque token. Only its hash is ever stored."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()
