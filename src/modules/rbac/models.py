from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    str_enum_column,
)
from src.modules.rbac.constants import ActionType

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        Uuid,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        Uuid,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("role_permissions_permission_id_idx", "permission_id"),
)


class Role(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False, default=99, server_default="99")

    permissions: Mapped[list[Permission]] = relationship(
        secondary=role_permissions, back_populates="roles", lazy="selectin"
    )

    __table_args__ = (Index("roles_deleted_at_idx", "deleted_at"),)


class Module(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "modules"

    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("modules.id", ondelete="SET NULL"),
        nullable=True,
    )

    parent: Mapped[Module | None] = relationship(remote_side="Module.id")

    __table_args__ = (
        Index("modules_parent_id_idx", "parent_id"),
        Index("modules_deleted_at_idx", "deleted_at"),
    )


class Permission(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "permissions"

    module_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
    )
    action: Mapped[ActionType] = str_enum_column(ActionType, nullable=False)

    module: Mapped[Module] = relationship(lazy="joined")
    roles: Mapped[list[Role]] = relationship(
        secondary=role_permissions, back_populates="permissions"
    )

    __table_args__ = (
        UniqueConstraint("module_id", "action", name="permissions_module_id_action_key"),
        Index("permissions_module_id_idx", "module_id"),
        Index("permissions_deleted_at_idx", "deleted_at"),
    )
