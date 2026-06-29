from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.dependencies import DbSession
from src.modules.logs import service
from src.modules.logs.schemas import (
    AuditLogFilters,
    AuditLogListResponse,
)
from src.modules.rbac.constants import ActionType
from src.modules.rbac.dependencies import require_permission
from src.pagination import PaginationParams, pagination_params

router = APIRouter(prefix="/logs")


@router.get(
    "/audit",
    response_model=AuditLogListResponse,
    dependencies=[Depends(require_permission("logs", ActionType.READ))],
)
async def list_audit_logs(
    db: DbSession,
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    filters: Annotated[AuditLogFilters, Query()],
):
    return await service.list_audit_logs(db, filters, pagination)
