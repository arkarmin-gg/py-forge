from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from src.dependencies import DbSession
from src.modules.rbac.constants import ActionType
from src.modules.rbac.dependencies import require_permission
from src.modules.settings import service
from src.modules.settings.exceptions import SettingNotFound
from src.modules.settings.schemas import SETTING_KEY_PATTERN, SettingRead, SettingUpsert

router = APIRouter(prefix="/settings")

SettingKeyPath = Annotated[
    str,
    Path(min_length=1, max_length=255, pattern=SETTING_KEY_PATTERN),
]


@router.get(
    "/",
    response_model=list[SettingRead],
    dependencies=[Depends(require_permission("settings", ActionType.READ))],
)
async def list_settings(db: DbSession):
    return await service.list_settings(db)


@router.get(
    "/{key}",
    response_model=SettingRead,
    dependencies=[Depends(require_permission("settings", ActionType.READ))],
)
async def get_setting(db: DbSession, key: SettingKeyPath):
    setting = await service.get_setting_by_key(db, key)
    if setting is None:
        raise SettingNotFound()
    return setting


@router.put(
    "/{key}",
    response_model=SettingRead,
    dependencies=[Depends(require_permission("settings", ActionType.UPDATE))],
)
async def upsert_setting(db: DbSession, key: SettingKeyPath, data: SettingUpsert):
    return await service.upsert_setting(db, key, data)


@router.delete(
    "/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("settings", ActionType.DELETE))],
)
async def delete_setting(db: DbSession, key: SettingKeyPath) -> None:
    await service.delete_setting(db, key)
