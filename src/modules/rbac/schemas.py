import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.modules.rbac.constants import ActionType
from src.schemas import BaseSchema


class ModuleRead(BaseSchema):
    id: uuid.UUID
    name: str
    code: str
    parent_id: uuid.UUID | None


class PermissionRead(BaseSchema):
    id: uuid.UUID
    action: ActionType
    module: ModuleRead


class RoleRead(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None
    rank: int
    permissions: list[PermissionRead]
    created_at: datetime


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    rank: int = Field(default=99, ge=1)
    permission_ids: list[uuid.UUID] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    rank: int | None = Field(default=None, ge=1)
    permission_ids: list[uuid.UUID] = Field(default_factory=list)


class RolePermissionsReplace(BaseModel):
    permission_ids: list[uuid.UUID] = Field(default_factory=list)
