from typing import Any

from sqlalchemy import ColumnElement, Select
from sqlalchemy.orm import InstrumentedAttribute

type Column = ColumnElement[Any] | InstrumentedAttribute[Any]


def where_if_not_none[StmtT: Select[Any]](
    stmt: StmtT, column: Column, value: object | None
) -> StmtT:
    if value is None:
        return stmt
    return stmt.where(column == value)


def where_gte_if_not_none[StmtT: Select[Any]](
    stmt: StmtT, column: Column, value: object | None
) -> StmtT:
    if value is None:
        return stmt
    return stmt.where(column >= value)


def where_lte_if_not_none[StmtT: Select[Any]](
    stmt: StmtT, column: Column, value: object | None
) -> StmtT:
    if value is None:
        return stmt
    return stmt.where(column <= value)
