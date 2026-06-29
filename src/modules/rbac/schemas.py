import uuid
from datetime import datetime

from pydantic import Field

from src.modules.rbac.constants import ActionType
from src.pagination import Page
from src.schemas import RequestSchema, ResponseSchema


class ModuleRead(ResponseSchema):
    id: uuid.UUID
    name: str
    code: str
    parent_id: uuid.UUID | None


class PermissionRead(ResponseSchema):
    id: uuid.UUID
    action: ActionType
    module: ModuleRead


class RoleRead(ResponseSchema):
    id: uuid.UUID
    name: str
    description: str | None
    rank: int
    permissions: list[PermissionRead]
    created_at: datetime


RoleListResponse = Page[RoleRead]


class RoleCreate(RequestSchema):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    rank: int = Field(default=99, ge=1)
    permission_ids: list[uuid.UUID] = Field(default_factory=list)


class RoleUpdate(RequestSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    rank: int | None = Field(default=None, ge=1)
    permission_ids: list[uuid.UUID] = Field(default_factory=list)
