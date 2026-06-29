import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.dependencies import DbSession
from src.modules.rbac import service
from src.modules.rbac.constants import ActionType
from src.modules.rbac.dependencies import require_permission
from src.modules.rbac.exceptions import RoleNotFound
from src.modules.rbac.schemas import (
    PermissionRead,
    RoleCreate,
    RoleListResponse,
    RoleRead,
    RoleUpdate,
)
from src.pagination import PaginationParams, pagination_params

router = APIRouter(prefix="/rbac")


@router.get(
    "/roles",
    response_model=RoleListResponse,
    dependencies=[Depends(require_permission("rbac", ActionType.READ))],
)
async def list_roles(
    db: DbSession,
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
):
    return await service.list_roles(db, pagination)


@router.post(
    "/roles",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("rbac", ActionType.CREATE))],
)
async def create_role(db: DbSession, data: RoleCreate):
    return await service.create_role(db, data)


@router.get(
    "/roles/{role_id}",
    response_model=RoleRead,
    dependencies=[Depends(require_permission("rbac", ActionType.READ))],
)
async def get_role(db: DbSession, role_id: uuid.UUID):
    role = await service.get_role_by_id(db, role_id)
    if role is None:
        raise RoleNotFound()
    return role


@router.patch(
    "/roles/{role_id}",
    response_model=RoleRead,
    dependencies=[Depends(require_permission("rbac", ActionType.UPDATE))],
)
async def update_role(db: DbSession, role_id: uuid.UUID, data: RoleUpdate):
    return await service.update_role(db, role_id, data)


@router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("rbac", ActionType.DELETE))],
)
async def delete_role(db: DbSession, role_id: uuid.UUID) -> None:
    await service.delete_role(db, role_id)


@router.get(
    "/permissions",
    response_model=list[PermissionRead],
    dependencies=[Depends(require_permission("rbac", ActionType.READ))],
)
async def list_permissions(db: DbSession):
    return await service.list_permissions(db)
