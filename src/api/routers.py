"""Top-level API router assembly.

Routes are split by audience inside the version prefix:
- ``/admin`` — administrative endpoints (admin console / back office).
- ``/app``   — public, mobile/frontend-facing endpoints (reserved, empty for now).
"""

from fastapi import APIRouter

from src.config import settings
from src.modules.admin_auth.router import router as auth_router
from src.modules.admins.router import router as admins_router

# Administrative endpoints. Auth here is admin auth (Admin model + RBAC).
admin_router = APIRouter(prefix="/admin")
admin_router.include_router(auth_router)
admin_router.include_router(admins_router)

# Public mobile/frontend endpoints. Reserved namespace — intentionally empty
# until the first app-facing module (and its own auth) exists.
app_router = APIRouter(prefix="/app")

v1 = APIRouter(prefix=settings.API_V1_PREFIX)
v1.include_router(admin_router)
v1.include_router(app_router)
