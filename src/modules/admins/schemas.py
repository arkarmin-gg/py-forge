import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from src.schemas import BaseSchema


class AdminRead(BaseSchema):
    """Public admin representation. Note: `password` is deliberately never included."""

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role_id: uuid.UUID
    profile_image_url: str | None
    is_banned: bool
    is_two_factor_enabled: bool
    last_login_at: datetime | None
    created_at: datetime


class AdminCreate(BaseModel):
    """Multipart form fields to create an admin. The plaintext password is hashed before
    storage; an optional `profile_image` file is accepted by the route separately.
    """

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role_id: uuid.UUID


class AdminUpdate(BaseModel):
    """Partial update. Only fields sent (and non-null) are applied; omitted fields are
    left untouched. NOT NULL columns can't be cleared through this endpoint by design.
    An optional `profile_image` file is accepted by the route separately.
    """

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role_id: uuid.UUID | None = None
    is_banned: bool | None = None


class AdminProfileUpdate(BaseModel):
    """Partial self-service profile update. Role, ban status, and password changes
    stay out of this schema because they have separate privilege or security rules.
    An optional `profile_image` file is accepted by the route separately.
    """

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
