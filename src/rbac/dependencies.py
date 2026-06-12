from collections.abc import Awaitable, Callable

from src.admins.models import Admin
from src.auth.dependencies import CurrentAdmin
from src.dependencies import DbSession
from src.rbac import service as rbac_service
from src.rbac.constants import ActionType
from src.rbac.exceptions import PermissionDenied


def require_permission(module_code: str, action: ActionType) -> Callable[..., Awaitable[Admin]]:
    """Dependency factory enforcing that the current admin's role grants `action` on `module_code`.

    Usage:
        dependencies=[Depends(require_permission("admins", ActionType.READ))]
    or to also receive the admin in the handler:
        admin: Annotated[Admin, Depends(require_permission("admins", ActionType.UPDATE))]
    """

    async def _guard(admin: CurrentAdmin, db: DbSession) -> Admin:
        if not await rbac_service.admin_has_permission(db, admin, module_code, action):
            raise PermissionDenied()
        return admin

    return _guard
