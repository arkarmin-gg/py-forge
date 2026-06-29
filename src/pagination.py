from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


class PaginationParams(BaseModel):
    limit: int = DEFAULT_PAGE_SIZE
    offset: int = 0


class Page[ItemT](BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[ItemT]
    total: int
    limit: int
    offset: int


def pagination_params(
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


async def paginate[ItemT](
    db: AsyncSession,
    stmt: Select[tuple[ItemT]],
    count_stmt: Select[tuple[int]],
    pagination: PaginationParams,
) -> Page[ItemT]:
    result = await db.execute(stmt.limit(pagination.limit).offset(pagination.offset))

    total = await db.scalar(count_stmt)

    return Page(
        items=list(result.scalars().all()),
        total=total or 0,
        limit=pagination.limit,
        offset=pagination.offset,
    )


async def get_all[ItemT](
    db: AsyncSession,
    stmt: Select[tuple[ItemT]],
) -> list[ItemT]:
    result = await db.execute(stmt)
    return list(result.scalars().all())
