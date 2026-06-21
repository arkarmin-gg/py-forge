"""Idempotent seed: a superadmin role with every permission, baseline modules, and an
initial admin account. Re-running it makes no duplicate rows.

    uv run python -m scripts.seed

Reads ADMIN_EMAIL / ADMIN_PASSWORD from the environment (see .env.example).
"""

import asyncio
import os

import src.registry  # noqa: F401  -- ensure all models are registered
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.database import SessionFactory
from src.modules.admin_auth import security
from src.modules.admins.models import Admin
from src.modules.rbac.constants import ActionType
from src.modules.rbac.models import Module, Permission, Role

# Baseline modules — one per domain. Extend as the app grows.
MODULE_CODES = ["admins", "users", "rbac", "logs", "settings"]


async def _get_or_create_superadmin_role(db: AsyncSession) -> Role:
    stmt = (
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.name == "superadmin")
    )

    role = (await db.execute(stmt)).scalar_one_or_none()

    if role is None:
        role = Role(
            name="superadmin",
            description="Full, unrestricted access.",
            rank=1,
            permissions=[],  # init the collection so accessing it never lazy-loads
        )
        db.add(role)
        await db.flush()

    return role


async def _ensure_modules_and_permissions(db: AsyncSession, role: Role) -> int:
    granted = 0

    existing_permission_ids = {permission.id for permission in role.permissions}

    for code in MODULE_CODES:
        module = (
            await db.execute(select(Module).where(Module.code == code))
        ).scalar_one_or_none()

        if module is None:
            module = Module(name=code.capitalize(), code=code)
            db.add(module)
            await db.flush()

        for action in ActionType:
            permission = (
                await db.execute(
                    select(Permission).where(
                        Permission.module_id == module.id,
                        Permission.action == action,
                    )
                )
            ).scalar_one_or_none()

            if permission is None:
                permission = Permission(module_id=module.id, action=action)
                db.add(permission)
                await db.flush()

            if permission.id not in existing_permission_ids:
                role.permissions.append(permission)
                existing_permission_ids.add(permission.id)
                granted += 1

    return granted


async def _ensure_initial_admin(db: AsyncSession, role: Role) -> tuple[str, bool]:
    email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    password = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
    admin = (
        await db.execute(select(Admin).where(Admin.email == email))
    ).scalar_one_or_none()
    if admin is not None:
        return email, False
    db.add(
        Admin(
            email=email,
            full_name="Super Admin",
            password=security.hash_password(password),
            role_id=role.id,
        )
    )
    return email, True


async def seed() -> None:
    async with SessionFactory() as db:
        role = await _get_or_create_superadmin_role(db)
        granted = await _ensure_modules_and_permissions(db, role)
        email, created = await _ensure_initial_admin(db, role)
        await db.commit()

    print(
        f"Seed complete: superadmin role ready, {len(MODULE_CODES)} modules, "
        f"+{granted} permission grant(s), "
        f"admin <{email}> {'created' if created else 'already existed'}."
    )


if __name__ == "__main__":
    asyncio.run(seed())
