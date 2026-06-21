import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.modules.admins.models import Admin
from src.modules.rbac.constants import ActionType
from src.modules.rbac.exceptions import (
    InvalidPermission,
    ProtectedRole,
    RoleAssigned,
    RoleNameConflict,
    RoleNotFound,
)
from src.modules.rbac.models import Module, Permission, Role, role_permissions
from src.modules.rbac.schemas import RoleCreate, RoleUpdate

SUPERADMIN_ROLE_NAME = "superadmin"


async def admin_has_permission(
    db: AsyncSession, admin: Admin, module_code: str, action: ActionType
) -> bool:
    """True if the admin's role grants `action` on the module identified by `module_code`.

    Soft-deleted permissions/modules are excluded automatically by the global filter,
    so a revoked module or permission can't accidentally grant access.
    """
    stmt = (
        select(Permission.id)
        .join(role_permissions, role_permissions.c.permission_id == Permission.id)
        .join(Module, Module.id == Permission.module_id)
        .where(
            role_permissions.c.role_id == admin.role_id,
            Module.code == module_code,
            Permission.action == action,
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.first() is not None


async def list_roles(db: AsyncSession) -> list[Role]:
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions).joinedload(Permission.module))
        .order_by(Role.rank.asc(), Role.name.asc())
    )
    return list(result.scalars().all())


async def list_permissions(db: AsyncSession) -> list[Permission]:
    result = await db.execute(
        select(Permission)
        .join(Permission.module)
        .options(joinedload(Permission.module))
        .order_by(Module.code.asc(), Permission.action.asc())
    )
    return list(result.scalars().all())


async def get_role_by_id(db: AsyncSession, role_id: uuid.UUID) -> Role | None:
    result = await db.execute(
        select(Role)
        .where(Role.id == role_id)
        .options(selectinload(Role.permissions).joinedload(Permission.module))
    )
    return result.scalar_one_or_none()


async def _require_role(db: AsyncSession, role_id: uuid.UUID) -> Role:
    role = await get_role_by_id(db, role_id)
    if role is None:
        raise RoleNotFound()
    return role


def _ensure_role_is_mutable(role: Role) -> None:
    if role.name == SUPERADMIN_ROLE_NAME:
        raise ProtectedRole()


async def _ensure_role_name_available(
    db: AsyncSession, name: str, role_id: uuid.UUID | None = None
) -> None:
    result = await db.execute(select(Role).where(Role.name == name))
    existing = result.scalar_one_or_none()
    if existing is not None and existing.id != role_id:
        raise RoleNameConflict()


async def _resolve_permissions(
    db: AsyncSession, permission_ids: list[uuid.UUID]
) -> list[Permission]:
    unique_permission_ids = set(permission_ids)
    if not unique_permission_ids:
        return []

    result = await db.execute(
        select(Permission)
        .where(Permission.id.in_(unique_permission_ids))
        .options(joinedload(Permission.module))
        .order_by(Permission.id.asc())
    )
    permissions = list(result.scalars().all())
    if len(permissions) != len(unique_permission_ids):
        raise InvalidPermission()
    return permissions


async def create_role(db: AsyncSession, data: RoleCreate) -> Role:
    await _ensure_role_name_available(db, data.name)
    permissions = await _resolve_permissions(db, data.permission_ids)
    role = Role(
        name=data.name,
        description=data.description,
        rank=data.rank,
        permissions=permissions,
    )
    db.add(role)
    await db.commit()
    created = await get_role_by_id(db, role.id)
    if created is None:
        raise RoleNotFound()
    return created


async def update_role(db: AsyncSession, role_id: uuid.UUID, data: RoleUpdate) -> Role:
    role = await _require_role(db, role_id)
    _ensure_role_is_mutable(role)

    should_replace_permissions = "permission_ids" in data.model_fields_set
    permissions = (
        await _resolve_permissions(db, data.permission_ids)
        if should_replace_permissions
        else None
    )

    fields = data.model_dump(exclude_unset=True)
    fields.pop("permission_ids", None)
    for key in ("name", "rank"):
        if fields.get(key) is None:
            fields.pop(key, None)

    new_name = fields.get("name")
    if new_name is not None and new_name != role.name:
        await _ensure_role_name_available(db, new_name, role_id=role.id)

    for key, value in fields.items():
        setattr(role, key, value)

    if should_replace_permissions:
        role.permissions = permissions or []

    await db.commit()
    updated = await get_role_by_id(db, role.id)
    if updated is None:
        raise RoleNotFound()
    return updated


async def delete_role(db: AsyncSession, role_id: uuid.UUID) -> None:
    role = await _require_role(db, role_id)
    _ensure_role_is_mutable(role)

    admin_count = await db.scalar(
        select(func.count()).select_from(Admin).where(Admin.role_id == role.id)
    )
    if admin_count:
        raise RoleAssigned()

    role.deleted_at = datetime.now(UTC)
    await db.commit()


async def replace_role_permissions(
    db: AsyncSession, role_id: uuid.UUID, permission_ids: list[uuid.UUID]
) -> Role:
    role = await _require_role(db, role_id)
    _ensure_role_is_mutable(role)

    permissions = await _resolve_permissions(db, permission_ids)
    role.permissions = permissions
    await db.commit()
    updated = await get_role_by_id(db, role.id)
    if updated is None:
        raise RoleNotFound()
    return updated
