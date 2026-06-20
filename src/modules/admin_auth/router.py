from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.dependencies import DbSession
from src.modules.admin_auth import service
from src.modules.admin_auth.dependencies import CurrentAdmin
from src.modules.admin_auth.schemas import RefreshRequest, TokenResponse
from src.modules.admins.schemas import AdminRead

router = APIRouter(prefix="/auth")


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
async def me(admin: CurrentAdmin) -> AdminRead:
    return admin
