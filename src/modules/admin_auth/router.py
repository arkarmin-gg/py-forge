from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm

from src.dependencies import DbSession, form_model
from src.modules.admin_auth import service
from src.modules.admin_auth.dependencies import CurrentAdmin
from src.modules.admin_auth.schemas import (
    ChangePasswordRequest,
    RefreshRequest,
    TokenResponse,
)
from src.modules.admins import service as admin_service
from src.modules.admins.schemas import AdminProfileUpdate, AdminRead

router = APIRouter(prefix="/auth")


async def _admin_profile_update_form(request: Request) -> AdminProfileUpdate:
    return await form_model(request, AdminProfileUpdate)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession
) -> TokenResponse:
    access_token, refresh_token = await service.login(db, form.username, form.password)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(body: RefreshRequest, db: DbSession) -> TokenResponse:
    access_token, refresh_token = await service.rotate_refresh_token(
        db, body.refresh_token
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(admin: CurrentAdmin, db: DbSession) -> None:
    await service.logout(db, admin.id)


@router.get("/me", response_model=AdminRead)
async def me(admin: CurrentAdmin):
    return admin


@router.patch("/me", response_model=AdminRead)
async def update_me(
    admin: CurrentAdmin,
    db: DbSession,
    data: Annotated[AdminProfileUpdate, Depends(_admin_profile_update_form)],
    profile_image: Annotated[UploadFile | None, File()] = None,
):
    return await admin_service.update_profile(
        db, admin.id, data, profile_image=profile_image
    )


@router.patch(
    "/me/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_my_password(
    admin: CurrentAdmin,
    db: DbSession,
    body: ChangePasswordRequest,
) -> None:
    await service.change_password(
        db,
        admin,
        current_password=body.current_password,
        new_password=body.new_password,
    )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_me(admin: CurrentAdmin, db: DbSession) -> None:
    await service.delete_me(db, admin)
