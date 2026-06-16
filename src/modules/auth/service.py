import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.admins import service as admin_service
from src.modules.admins.models import Admin
from src.modules.auth import security
from src.modules.auth.config import auth_settings
from src.modules.auth.exceptions import InactiveAdmin, InvalidCredentials, InvalidToken
from src.modules.auth.models import RefreshToken


async def authenticate_admin(db: AsyncSession, email: str, password: str) -> Admin:
    admin = await admin_service.get_by_email(db, email)
    if admin is None or admin.password is None:
        raise InvalidCredentials()
    if not security.verify_password(password, admin.password):
        raise InvalidCredentials()
    if admin.is_banned:
        raise InactiveAdmin()
    return admin


async def _issue_refresh_token(db: AsyncSession, admin_id: uuid.UUID) -> str:
    raw = security.generate_refresh_token()
    db.add(
        RefreshToken(
            token_hash=security.hash_refresh_token(raw),
            admin_id=admin_id,
            expires_at=datetime.now(UTC) + timedelta(days=auth_settings.REFRESH_TOKEN_EXP_DAYS),
        )
    )
    return raw


async def login(db: AsyncSession, email: str, password: str) -> tuple[str, str]:
    admin = await authenticate_admin(db, email, password)
    access_token = security.create_access_token(str(admin.id))
    refresh_token = await _issue_refresh_token(db, admin.id)
    admin.last_login_at = datetime.now(UTC)
    await db.commit()
    return access_token, refresh_token


async def rotate_refresh_token(db: AsyncSession, raw_token: str) -> tuple[str, str]:
    """Revoke the presented refresh token and issue a fresh access + refresh pair."""
    token_hash = security.hash_refresh_token(raw_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored = result.scalar_one_or_none()
    now = datetime.now(UTC)
    if (
        stored is None
        or stored.is_revoked
        or stored.admin_id is None
        or (stored.expires_at is not None and stored.expires_at < now)
    ):
        raise InvalidToken()

    admin = await admin_service.get_by_id(db, stored.admin_id)
    if admin is None or admin.is_banned:
        raise InvalidToken()

    stored.is_revoked = True  # rotation: the old token is single-use
    access_token = security.create_access_token(str(admin.id))
    refresh_token = await _issue_refresh_token(db, admin.id)
    await db.commit()
    return access_token, refresh_token


async def logout(db: AsyncSession, admin_id: uuid.UUID) -> None:
    """Revoke all of the admin's active refresh tokens."""
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.admin_id == admin_id, RefreshToken.is_revoked.is_(False))
        .values(is_revoked=True)
    )
    admin = await admin_service.get_by_id(db, admin_id)
    if admin is not None:
        admin.last_logout_at = datetime.now(UTC)
    await db.commit()
