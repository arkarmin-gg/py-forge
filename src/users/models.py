from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    str_enum_column,
)
from src.users.constants import LoginProvider, RegistrationStage


class User(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"

    email: Mapped[str | None] = mapped_column(String, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # SMS auth identity
    # hashed (argon2); nullable until the user sets one. Never serialized.
    password: Mapped[str | None] = mapped_column(String, nullable=True)
    is_banned: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    profile_image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    date_of_birth: Mapped[str | None] = mapped_column(String, nullable=True)
    gender: Mapped[str | None] = mapped_column(String, nullable=True)
    prefer_language: Mapped[str | None] = mapped_column(String, nullable=True)
    registration_stage: Mapped[RegistrationStage] = str_enum_column(
        RegistrationStage,
        nullable=False,
        default=RegistrationStage.OTP_VERIFIED,
        server_default=RegistrationStage.OTP_VERIFIED.value,
    )
    fcm_token: Mapped[str | None] = mapped_column(String, nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_logout_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    apple_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    login_provider: Mapped[LoginProvider | None] = str_enum_column(LoginProvider, nullable=True)

    __table_args__ = (
        Index("users_email_idx", "email"),
        Index("users_full_name_idx", "full_name"),
        Index("users_is_banned_idx", "is_banned"),
        Index("users_deleted_at_idx", "deleted_at"),
    )
