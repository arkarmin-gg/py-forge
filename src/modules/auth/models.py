import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base, TimestampMixin, UUIDPrimaryKeyMixin, str_enum_column
from src.modules.auth.constants import OtpPurpose, OtpStatus

# Polymorphic owner: exactly one of user_id / admin_id is set, enforced by a CHECK
# (DBML can't express this — see DATABASE_ERD.dbml). XOR via "<>" on the two NOT NULL tests.
_OWNER_XOR = "(user_id IS NOT NULL) <> (admin_id IS NOT NULL)"


class RefreshToken(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "refresh_tokens"

    token_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    admin_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("admins.id", ondelete="CASCADE"), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    __table_args__ = (
        CheckConstraint(_OWNER_XOR, name="owner"),
        Index("refresh_tokens_token_hash_idx", "token_hash"),
        Index("refresh_tokens_user_id_idx", "user_id"),
        Index("refresh_tokens_admin_id_idx", "admin_id"),
        Index("refresh_tokens_expires_at_idx", "expires_at"),
        Index("refresh_tokens_user_id_is_revoked_idx", "user_id", "is_revoked"),
        Index("refresh_tokens_admin_id_is_revoked_idx", "admin_id", "is_revoked"),
    )


class OtpRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "otp_records"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    admin_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("admins.id", ondelete="CASCADE"), nullable=True
    )
    status: Mapped[OtpStatus] = str_enum_column(
        OtpStatus,
        nullable=False,
        default=OtpStatus.PENDING,
        server_default=OtpStatus.PENDING.value,
    )
    purpose: Mapped[OtpPurpose] = str_enum_column(OtpPurpose, nullable=False)
    code_hash: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    request_id: Mapped[str | None] = mapped_column(String, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    max_attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3, server_default="3"
    )

    __table_args__ = (
        CheckConstraint(_OWNER_XOR, name="owner"),
        Index("otp_records_user_id_idx", "user_id"),
        Index("otp_records_admin_id_idx", "admin_id"),
        Index("otp_records_expires_at_idx", "expires_at"),
        Index("otp_records_user_id_purpose_status_idx", "user_id", "purpose", "status"),
        Index("otp_records_admin_id_purpose_status_idx", "admin_id", "purpose", "status"),
    )
