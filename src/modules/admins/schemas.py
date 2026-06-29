import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator

from src.pagination import Page
from src.schemas import RequestSchema, ResponseSchema


class AdminRead(ResponseSchema):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role_id: uuid.UUID
    profile_image_url: str | None
    is_banned: bool
    is_two_factor_enabled: bool
    last_login_at: datetime | None
    last_logout_at: datetime | None
    created_at: datetime
    updated_at: datetime


AdminListResponse = Page[AdminRead]


class AdminCreate(RequestSchema):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role_id: uuid.UUID


class AdminUpdate(RequestSchema):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role_id: uuid.UUID | None = None
    is_banned: bool | None = None

    @model_validator(mode="after")
    def at_least_one_field_required(self):
        if all(
            value is None
            for value in [
                self.full_name,
                self.email,
                self.password,
                self.is_banned,
                self.role_id,
            ]
        ):
            raise ValueError("At least one field must be provided for update")

        return self


class AdminProfileUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)

    @model_validator(mode="after")
    def at_least_one_field_required(self):
        if all(
            value is None
            for value in [
                self.full_name,
                self.email,
            ]
        ):
            raise ValueError("At least one field must be provided for update")

        return self
