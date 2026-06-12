from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.admins.schemas import AdminRead
from src.auth import service
from src.auth.dependencies import CurrentAdmin
from src.auth.schemas import RefreshRequest, TokenResponse
from src.dependencies import DbSession
from src.schemas import ErrorResponse

router = APIRouter(prefix="/auth", tags=["auth"])

_AUTH_ERRORS = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse, "description": "Authentication failed"},
}


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Admin login",
    description="Exchange admin email (as `username`) + password for an access + refresh token.",
    responses=_AUTH_ERRORS,
)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession
) -> TokenResponse:
    access_token, refresh_token = await service.login(db, form.username, form.password)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate refresh token",
    description="Exchange a valid refresh token for a new pair; the old token is revoked.",
    responses=_AUTH_ERRORS,
)
async def refresh(body: RefreshRequest, db: DbSession) -> TokenResponse:
    access_token, refresh_token = await service.rotate_refresh_token(db, body.refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout",
    description="Revoke all of the current admin's active refresh tokens.",
    responses=_AUTH_ERRORS,
)
async def logout(admin: CurrentAdmin, db: DbSession) -> None:
    await service.logout(db, admin.id)


@router.get(
    "/me",
    response_model=AdminRead,
    summary="Current admin",
    responses=_AUTH_ERRORS,
)
async def me(admin: CurrentAdmin) -> AdminRead:
    return admin
