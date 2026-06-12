import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from src.admins import service
from src.admins.exceptions import AdminNotFound
from src.admins.schemas import AdminCreate, AdminRead, AdminUpdate
from src.dependencies import DbSession
from src.rbac.constants import ActionType
from src.rbac.dependencies import require_permission

router = APIRouter(
    prefix="/admins",
)


@router.get(
    "/",
    response_model=list[AdminRead],
    dependencies=[Depends(require_permission("admins", ActionType.READ))],
)
async def list_admins(db: DbSession):
    return await service.list_admins(db)


@router.post(
    "/",
    response_model=AdminRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("admins", ActionType.CREATE))],
)
async def create_admin(db: DbSession, data: AdminCreate):
    return await service.create(db, data)


@router.get(
    "/{admin_id}",
    response_model=AdminRead,
    dependencies=[Depends(require_permission("admins", ActionType.READ))],
)
async def get_by_id(db: DbSession, admin_id: uuid.UUID):
    admin = await service.get_by_id(db, admin_id)
    if admin is None:
        raise AdminNotFound()
    return admin


@router.patch(
    "/{admin_id}",
    response_model=AdminRead,
    dependencies=[Depends(require_permission("admins", ActionType.UPDATE))],
)
async def update_admin(db: DbSession, admin_id: uuid.UUID, data: AdminUpdate):
    return await service.update(db, admin_id, data)


@router.delete(
    "/{admin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("admins", ActionType.DELETE))],
)
async def delete_admin(db: DbSession, admin_id: uuid.UUID):
    await service.delete(db, admin_id)


@router.put(
    "/{admin_id}/profile-image",
    response_model=AdminRead,
    dependencies=[Depends(require_permission("admins", ActionType.UPDATE))],
)
async def set_profile_image(
    db: DbSession, admin_id: uuid.UUID, file: Annotated[UploadFile, File()]
):
    return await service.set_profile_image(db, admin_id, file)


@router.delete(
    "/{admin_id}/profile-image",
    response_model=AdminRead,
    dependencies=[Depends(require_permission("admins", ActionType.UPDATE))],
)
async def remove_profile_image(db: DbSession, admin_id: uuid.UUID):
    return await service.remove_profile_image(db, admin_id)
