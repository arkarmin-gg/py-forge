import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base, str_enum_column
from src.modules.logs.constants import LogAction, LogStatus

# High-volume, append-only tables: integer PK, single created_at, no soft delete.
# Consider range partitioning on created_at if these grow large.


class ActivityLog(Base):
    """A single action taken by a User."""

    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[LogAction] = str_enum_column(LogAction, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String, nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
    device: Mapped[str | None] = mapped_column(String, nullable=True)
    browser: Mapped[str | None] = mapped_column(String, nullable=True)
    os: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[LogStatus] = str_enum_column(
        LogStatus,
        nullable=False,
        default=LogStatus.SUCCESS,
        server_default=LogStatus.SUCCESS.value,
    )
    # "metadata" is reserved on Declarative Base, so the attribute is `meta`.
    meta: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index(
            "activity_logs_user_id_action_created_at_idx",
            "user_id",
            "action",
            "created_at",
        ),
    )


class AuditLog(Base):
    """A single action taken by an Admin, with before/after state."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # SET NULL: audit history survives admin deletion.
    admin_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
    )
    action: Mapped[LogAction] = str_enum_column(LogAction, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    entity_name: Mapped[str | None] = mapped_column(String, nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String, nullable=True)
    old_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
    device: Mapped[str | None] = mapped_column(String, nullable=True)
    browser: Mapped[str | None] = mapped_column(String, nullable=True)
    os: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[LogStatus] = str_enum_column(
        LogStatus,
        nullable=False,
        default=LogStatus.SUCCESS,
        server_default=LogStatus.SUCCESS.value,
    )
    meta: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index(
            "audit_logs_admin_id_action_created_at_idx",
            "admin_id",
            "action",
            "created_at",
        ),
        Index("audit_logs_entity_name_entity_id_idx", "entity_name", "entity_id"),
    )
