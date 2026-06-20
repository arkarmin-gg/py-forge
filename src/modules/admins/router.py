import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, UploadFile, status

from src.dependencies import DbSession, form_model
from src.modules.admins import service
from src.modules.admins.exceptions import AdminNotFound
from src.modules.admins.schemas import AdminCreate, AdminRead, AdminUpdate
from src.modules.rbac.constants import ActionType
from src.modules.rbac.dependencies import require_permission

router = APIRouter(
    prefix="/admins",
)


async def _admin_create_form(request: Request) -> AdminCreate:
    return await form_model(request, AdminCreate)


async def _admin_update_form(request: Request) -> AdminUpdate:
    return await form_model(request, AdminUpdate)


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
async def create_admin(
    db: DbSession,
    data: Annotated[AdminCreate, Depends(_admin_create_form)],
    profile_image: Annotated[UploadFile | None, File()] = None,
):
    return await service.create(db, data, profile_image=profile_image)


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
async def update_admin(
    db: DbSession,
    admin_id: uuid.UUID,
    data: Annotated[AdminUpdate, Depends(_admin_update_form)],
    profile_image: Annotated[UploadFile | None, File()] = None,
):
    return await service.update(db, admin_id, data, profile_image=profile_image)


@router.delete(
    "/{admin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("admins", ActionType.DELETE))],
)
async def delete_admin(db: DbSession, admin_id: uuid.UUID):
    await service.delete(db, admin_id)


@router.delete(
    "/{admin_id}/profile-image",
    response_model=AdminRead,
    dependencies=[Depends(require_permission("admins", ActionType.UPDATE))],
)
async def remove_profile_image(db: DbSession, admin_id: uuid.UUID):
    return await service.remove_profile_image(db, admin_id)
