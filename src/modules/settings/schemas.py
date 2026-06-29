import uuid
from datetime import datetime
from typing import Annotated, Any

from pydantic import Field

from src.schemas import RequestSchema, ResponseSchema

SETTING_KEY_PATTERN = r"^[a-z0-9][a-z0-9_.-]{0,254}$"

SettingKey = Annotated[
    str,
    Field(
        min_length=1,
        max_length=255,
        pattern=SETTING_KEY_PATTERN,
    ),
]


class SettingRead(ResponseSchema):
    id: uuid.UUID
    key: str
    value: dict[str, Any]
    description: str | None
    created_at: datetime
    updated_at: datetime


class SettingUpsert(RequestSchema):
    value: dict[str, Any]
    description: str | None = None
