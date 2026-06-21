import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, MetaData, Uuid, func, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Postgres-friendly, deterministic constraint/index names (see FASTAPI_BEST_PRACTICES.md).
NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class UUIDPrimaryKeyMixin:
    """uuid PK generated server-side by Postgres gen_random_uuid() (built into PG 13+)."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class SoftDeleteMixin:
    """Marker + column for soft delete. Filtering is automatic (see ADR 0002 and database.py)."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )


def str_enum_column[EnumT: StrEnum](
    enum_cls: type[EnumT], length: int = 50, **kwargs: object
) -> Mapped:
    """A VARCHAR-backed enum column (see ADR 0001).

    Stores the StrEnum's *value*. No native Postgres ENUM type and no CHECK constraint,
    so adding a new member is a code-only change with no migration.
    """
    return mapped_column(
        SAEnum(
            enum_cls,
            native_enum=False,
            length=length,
            values_callable=lambda e: [member.value for member in e],
            validate_strings=True,
        ),
        **kwargs,
    )
