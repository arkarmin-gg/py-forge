import uuid
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.config import settings
from src.dependencies import DbSession
from src.modules.admins import service as admin_service
from src.modules.admins.models import Admin
from src.modules.auth import security
from src.modules.auth.exceptions import InactiveAdmin, InvalidToken

# tokenUrl powers the Swagger "Authorize" button (form login at the admin auth router).
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/admin/auth/login"
)


async def get_current_admin(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> Admin:
    try:
        payload = security.decode_access_token(token)
    except jwt.InvalidTokenError as exc:
        raise InvalidToken() from exc

    if payload.get("type") != "access":
        raise InvalidToken()

    subject = payload.get("sub")
    if subject is None:
        raise InvalidToken()
    try:
        admin_id = uuid.UUID(subject)
    except ValueError as exc:
        raise InvalidToken() from exc

    admin = await admin_service.get_by_id(db, admin_id)
    if admin is None:
        raise InvalidToken()
    if admin.is_banned:
        raise InactiveAdmin()
    return admin


CurrentAdmin = Annotated[Admin, Depends(get_current_admin)]
