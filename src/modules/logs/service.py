from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.logs.models import AuditLog
from src.modules.logs.schemas import AuditLogFilters
from src.pagination import Page, PaginationParams, paginate
from src.query_filters import (
    where_gte_if_not_none,
    where_if_not_none,
    where_lte_if_not_none,
)


def _apply_audit_log_filters[StmtT: Select[Any]](stmt: StmtT, filters: AuditLogFilters) -> StmtT:
    stmt = where_if_not_none(stmt, AuditLog.admin_id, filters.admin_id)
    stmt = where_if_not_none(stmt, AuditLog.action, filters.action)
    stmt = where_if_not_none(stmt, AuditLog.status, filters.status)
    stmt = where_gte_if_not_none(stmt, AuditLog.created_at, filters.created_from)
    stmt = where_lte_if_not_none(stmt, AuditLog.created_at, filters.created_to)

    return stmt


async def list_audit_logs(
    db: AsyncSession, filters: AuditLogFilters, pagination: PaginationParams
) -> Page[AuditLog]:
    filtered = _apply_audit_log_filters(select(AuditLog), filters)

    stmt = filtered.order_by(AuditLog.created_at.desc(), AuditLog.id.desc())

    count_stmt = _apply_audit_log_filters(select(func.count(AuditLog.id)), filters)

    return await paginate(db, stmt, count_stmt, pagination)
