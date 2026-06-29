"""Top-level API router assembly.

Routes are split by audience inside the version prefix:
- ``/admin`` — administrative endpoints (admin console / back office).
- ``/app``   — mobile/frontend-facing endpoints.
"""

from fastapi import APIRouter

from src.config import settings
from src.modules.admins.router import router as admins_router
from src.modules.auth.router import router as auth_router
from src.modules.logs.router import router as logs_router
from src.modules.rbac.router import router as rbac_router
from src.modules.settings.router import router as settings_router

# Administrative endpoints. Auth here is admin auth (Admin model + RBAC).
admin_router = APIRouter(prefix="/admin")
admin_router.include_router(auth_router)
admin_router.include_router(admins_router)
admin_router.include_router(logs_router)
admin_router.include_router(rbac_router)
admin_router.include_router(settings_router)

# Public mobile/frontend endpoints. Reserved namespace — intentionally empty
# until the first app-facing module (and its own auth) exists.
app_router = APIRouter(prefix="/app")

v1 = APIRouter(prefix=settings.API_V1_PREFIX)
v1.include_router(admin_router)
v1.include_router(app_router)
