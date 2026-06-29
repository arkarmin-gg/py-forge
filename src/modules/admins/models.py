import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from src.modules.rbac.models import Role


class Admin(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "admins"

    full_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    password: Mapped[str | None] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    profile_image_key: Mapped[str | None] = mapped_column(String, nullable=True)
    role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    is_banned: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    is_two_factor_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_logout_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    role: Mapped[Role] = relationship(lazy="joined")

    @property
    def profile_image_url(self) -> str | None:
        from src.storage.service import presigned_url

        return presigned_url(self.profile_image_key)

    __table_args__ = (
        Index("admins_email_idx", "email"),
        Index("admins_full_name_idx", "full_name"),
        Index("admins_is_banned_idx", "is_banned"),
        Index("admins_role_id_idx", "role_id"),
        Index("admins_deleted_at_idx", "deleted_at"),
    )
