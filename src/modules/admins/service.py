import uuid
from contextlib import suppress
from datetime import UTC, datetime

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.admins.exceptions import AdminEmailConflict, AdminNotFound, InvalidRole
from src.modules.admins.models import Admin
from src.modules.admins.schemas import AdminCreate, AdminUpdate
from src.modules.auth import security
from src.modules.rbac.models import Role
from src.storage import service as storage
from src.storage.exceptions import StorageError


async def get_by_id(db: AsyncSession, admin_id: uuid.UUID) -> Admin | None:
    return await db.get(Admin, admin_id)


async def get_by_email(db: AsyncSession, email: str) -> Admin | None:
    result = await db.execute(select(Admin).where(Admin.email == email))
    return result.scalar_one_or_none()


async def list_admins(db: AsyncSession) -> list[Admin]:
    result = await db.execute(select(Admin).order_by(Admin.created_at.desc()))
    return list(result.scalars().all())


async def _ensure_role_exists(db: AsyncSession, role_id: uuid.UUID) -> None:
    """Surface a clean 422 instead of an opaque FK IntegrityError at commit."""
    if await db.get(Role, role_id) is None:
        raise InvalidRole()


async def create(db: AsyncSession, data: AdminCreate) -> Admin:
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
    await db.commit()
    await db.refresh(admin)  # populate server defaults (id, created_at, ...)
    return admin


async def update(db: AsyncSession, admin_id: uuid.UUID, data: AdminUpdate) -> Admin:
    admin = await get_by_id(db, admin_id)
    if admin is None:
        raise AdminNotFound()

    # exclude_unset drops omitted fields; dropping None protects NOT NULL columns.
    fields = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}

    password = fields.pop("password", None)
    if password is not None:
        admin.password = security.hash_password(password)

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

    await db.commit()
    await db.refresh(admin)
    return admin


async def delete(db: AsyncSession, admin_id: uuid.UUID) -> None:
    """Soft delete: stamp deleted_at. The global filter hides it from future reads,
    so re-deleting an already-deleted admin is a clean 404 (get_by_id returns None).
    """
    admin = await get_by_id(db, admin_id)
    if admin is None:
        raise AdminNotFound()
    admin.deleted_at = datetime.now(UTC)
    await db.commit()


def _avatar_prefix(admin_id: uuid.UUID) -> str:
    return f"admins/{admin_id}/avatar"


async def set_profile_image(
    db: AsyncSession, admin_id: uuid.UUID, file: UploadFile
) -> Admin:
    """Upload (or replace) the admin's profile image. Validates type/size, stores the
    new object, swaps the key, and best-effort removes the previous object."""
    admin = await get_by_id(db, admin_id)
    if admin is None:
        raise AdminNotFound()

    stored = await storage.replace_image(
        admin.profile_image_key, file, prefix=_avatar_prefix(admin_id)
    )
    admin.profile_image_key = stored.key
    await db.commit()
    await db.refresh(admin)
    return admin


async def remove_profile_image(db: AsyncSession, admin_id: uuid.UUID) -> Admin:
    """Clear the admin's profile image. Idempotent: no image is a no-op, not a 404.

    The DB reference is cleared and committed first (so it's never left dangling), then
    the object is deleted best-effort — a failed object delete leaves an orphan, not a
    broken reference.
    """
    admin = await get_by_id(db, admin_id)
    if admin is None:
        raise AdminNotFound()

    old_key = admin.profile_image_key
    if old_key is None:
        return admin

    admin.profile_image_key = None
    await db.commit()
    await db.refresh(admin)
    # orphaned object on failure is fine; sweep later rather than fail a succeeded removal
    with suppress(StorageError):
        await storage.delete(old_key)
    return admin
