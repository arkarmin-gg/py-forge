from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import ORMExecuteState, Session, with_loader_criteria

from src.config import settings
from src.models import SoftDeleteMixin

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
)

SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


@event.listens_for(Session, "do_orm_execute")
def _filter_soft_deleted(state: ORMExecuteState) -> None:
    if (
        state.is_select
        and not state.is_column_load
        and not state.is_relationship_load
        and not state.execution_options.get("include_deleted", False)
    ):
        state.statement = state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True,
            )
        )


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    async with SessionFactory() as session:
        yield session
