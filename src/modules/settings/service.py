from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.settings.exceptions import SettingNotFound
from src.modules.settings.models import Setting
from src.modules.settings.schemas import SettingUpsert


async def list_settings(db: AsyncSession) -> list[Setting]:
    result = await db.execute(select(Setting).order_by(Setting.key.asc()))
    return list(result.scalars().all())


async def get_setting_by_key(db: AsyncSession, key: str) -> Setting | None:
    result = await db.execute(select(Setting).where(Setting.key == key))
    return result.scalar_one_or_none()


async def _get_setting_by_key_including_deleted(db: AsyncSession, key: str) -> Setting | None:
    result = await db.execute(
        select(Setting).where(Setting.key == key).execution_options(include_deleted=True)
    )
    return result.scalar_one_or_none()


async def upsert_setting(db: AsyncSession, key: str, data: SettingUpsert) -> Setting:
    setting = await _get_setting_by_key_including_deleted(db, key)

    if setting is None:
        setting = Setting(key=key, value=data.value, description=data.description)
        db.add(setting)
    else:
        setting.value = data.value
        setting.deleted_at = None
        if "description" in data.model_fields_set:
            setting.description: str | None = data.description

    await db.commit()
    await db.refresh(setting)
    return setting


async def delete_setting(db: AsyncSession, key: str) -> None:
    setting = await get_setting_by_key(db, key)
    if setting is None:
        raise SettingNotFound()

    setting.deleted_at = datetime.now(UTC)
    await db.commit()
