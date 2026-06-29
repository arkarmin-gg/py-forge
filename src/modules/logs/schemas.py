import uuid
from datetime import datetime
from typing import Any

from src.modules.logs.constants import LogAction, LogStatus
from src.pagination import Page
from src.schemas import RequestSchema, ResponseSchema


class AuditLogFilters(RequestSchema):
    admin_id: uuid.UUID | None = None
    action: LogAction | None = None
    status: LogStatus | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None


class AuditLogListItem(ResponseSchema):
    id: int
    admin_id: uuid.UUID | None
    action: LogAction
    description: str
    entity_name: str | None
    entity_id: str | None
    ip_address: str | None
    user_agent: str | None
    device: str | None
    browser: str | None
    os: str | None
    location: str | None
    status: LogStatus
    created_at: datetime


class AuditLogRead(AuditLogListItem):
    old_value: dict[str, Any] | None
    new_value: dict[str, Any] | None
    meta: dict[str, Any] | None


AuditLogListResponse = Page[AuditLogListItem]
