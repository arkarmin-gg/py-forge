from sqlalchemy import Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Setting(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """A system-wide configuration entry: a unique key with a JSON value."""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (Index("settings_deleted_at_idx", "deleted_at"),)
