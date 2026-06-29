import uuid
from contextlib import suppress
from datetime import UTC, datetime

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.admins.exceptions import AdminEmailConflict, AdminNotFound, InvalidRole
from src.modules.admins.models import Admin
from src.modules.admins.schemas import AdminCreate, AdminProfileUpdate, AdminUpdate
from src.modules.auth import security
from src.modules.rbac.models import Role
from src.pagination import Page, PaginationParams, paginate
from src.storage import service as storage
from src.storage.exceptions import StorageError


async def get_by_id(db: AsyncSession, admin_id: uuid.UUID) -> Admin | None:
    return await db.get(Admin, admin_id)


async def get_by_email(db: AsyncSession, email: str) -> Admin | None:
    result = await db.execute(select(Admin).where(Admin.email == email))
    return result.scalar_one_or_none()


async def list_admins(db: AsyncSession, pagination: PaginationParams) -> Page[Admin]:
    stmt = select(Admin).order_by(Admin.created_at.desc())
    count_stmt = select(func.count(Admin.id))

    return await paginate(db, stmt, count_stmt, pagination)


async def create(
    db: AsyncSession, data: AdminCreate, profile_image: UploadFile | None = None
) -> Admin:
    if await get_by_email(db, data.email) is not None:
        raise AdminEmailConflict()

    await _ensure_role_exists(db, data.role_id)

    admin = Admin(
        email=data.email,
        full_name=data.full_name,
        password=security.hash_password(data.password),
        role_id=data.role_id,
    )

    db.add(admin)

    if profile_image is not None:
        await db.flush()
        stored = await storage.upload_image(profile_image, prefix=_avatar_prefix(admin.id))
        admin.profile_image_key = stored.key

    await db.commit()
    await db.refresh(admin)
    return admin


async def update(
    db: AsyncSession,
    admin_id: uuid.UUID,
    data: AdminUpdate | None,
    profile_image: UploadFile | None = None,
) -> Admin:
    admin = await get_by_id(db, admin_id)
    if admin is None:
        raise AdminNotFound()

    fields = {}

    if data is not None:
        fields = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}

    new_password = fields.pop("password", None)
    if new_password is not None:
        admin.password = security.hash_password(new_password)

    new_email = fields.get("email")
    if new_email is not None and new_email != admin.email:
        existing = await get_by_email(db, new_email)
        if existing is not None and existing.id != admin.id:
            raise AdminEmailConflict()

    new_role_id = fields.get("role_id")
    if new_role_id is not None and new_role_id != admin.role_id:
        await _ensure_role_exists(db, new_role_id)

    for key, value in fields.items():
        setattr(admin, key, value)

    old_profile_image_key = admin.profile_image_key
    if profile_image is not None:
        stored = await storage.upload_image(profile_image, prefix=_avatar_prefix(admin_id))
        admin.profile_image_key = stored.key

    await db.commit()
    await db.refresh(admin)

    if (
        profile_image is not None
        and old_profile_image_key is not None
        and old_profile_image_key != admin.profile_image_key
    ):
        with suppress(StorageError):
            await storage.delete(old_profile_image_key)

    return admin


async def update_profile(
    db: AsyncSession,
    admin_id: uuid.UUID,
    data: AdminProfileUpdate | None,
    profile_image: UploadFile | None = None,
) -> Admin:
    admin = await get_by_id(db, admin_id)
    if admin is None:
        raise AdminNotFound()

    fields = {}

    if data is not None:
        fields = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}

    new_email = fields.get("email")
    if new_email is not None and new_email != admin.email:
        existing = await get_by_email(db, new_email)
        if existing is not None and existing.id != admin.id:
            raise AdminEmailConflict()

    for key, value in fields.items():
        setattr(admin, key, value)

    old_profile_image_key = admin.profile_image_key
    if profile_image is not None:
        stored = await storage.upload_image(profile_image, prefix=_avatar_prefix(admin_id))
        admin.profile_image_key = stored.key

    await db.commit()
    await db.refresh(admin)

    if (
        profile_image is not None
        and old_profile_image_key is not None
        and old_profile_image_key != admin.profile_image_key
    ):
        with suppress(StorageError):
            await storage.delete(old_profile_image_key)

    return admin


async def delete(db: AsyncSession, admin_id: uuid.UUID) -> None:
    admin = await get_by_id(db, admin_id)
    if admin is None:
        raise AdminNotFound()

    admin.deleted_at = datetime.now(UTC)

    await db.commit()


async def remove_profile_image(db: AsyncSession, admin_id: uuid.UUID) -> Admin:
    admin = await get_by_id(db, admin_id)
    if admin is None:
        raise AdminNotFound()

    old_key = admin.profile_image_key
    if old_key is None:
        return admin

    admin.profile_image_key = None
    await db.commit()
    await db.refresh(admin)

    with suppress(StorageError):
        await storage.delete(old_key)

    return admin


def _avatar_prefix(admin_id: uuid.UUID) -> str:
    return f"admins/{admin_id}/avatar"


async def _ensure_role_exists(db: AsyncSession, role_id: uuid.UUID) -> None:
    if await db.get(Role, role_id) is None:
        raise InvalidRole()
