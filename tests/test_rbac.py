import uuid

from src.modules.rbac import service as rbac_service
from src.modules.rbac.constants import ActionType


class _FakeResult:
    def __init__(self, row: object) -> None:
        self._row = row

    def first(self) -> object:
        return self._row


class _FakeSession:
    """Minimal stand-in for AsyncSession.execute — returns a canned result row."""

    def __init__(self, row: object) -> None:
        self._row = row

    async def execute(self, _stmt: object) -> _FakeResult:
        return _FakeResult(self._row)


class _FakeAdmin:
    role_id = uuid.uuid4()


async def test_admin_has_permission_true_when_grant_exists() -> None:
    db = _FakeSession(row=(uuid.uuid4(),))
    granted = await rbac_service.admin_has_permission(db, _FakeAdmin(), "admins", ActionType.READ)
    assert granted is True


async def test_admin_has_permission_false_when_no_grant() -> None:
    db = _FakeSession(row=None)
    granted = await rbac_service.admin_has_permission(db, _FakeAdmin(), "admins", ActionType.READ)
    assert granted is False
