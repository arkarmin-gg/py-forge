from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.admins.models import Admin
from src.modules.rbac.constants import ActionType
from src.modules.rbac.models import Module, Permission, role_permissions


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
