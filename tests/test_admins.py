import uuid

import pytest
from src.modules.admins import service
from src.modules.admins.exceptions import AdminEmailConflict, AdminNotFound, InvalidRole
from src.modules.admins.models import Admin
from src.modules.admins.schemas import AdminCreate, AdminUpdate
from src.modules.rbac.models import Role
from src.storage.schemas import StoredObject


class _Result:
    def __init__(self, scalar: object) -> None:
        self._scalar = scalar

    def scalar_one_or_none(self) -> object:
        return self._scalar


class _FakeSession:
    """Stand-in for AsyncSession. `get_map` keys lookups by model class;
    `execute_scalar` is what scalar_one_or_none() returns (used by get_by_email).
    """

    def __init__(
        self, *, get_map: dict | None = None, execute_scalar: object = None
    ) -> None:
        self._get_map = get_map or {}
        self._execute_scalar = execute_scalar
        self.committed = False

    async def get(self, model: type, _pk: object) -> object:
        return self._get_map.get(model)

    async def execute(self, _stmt: object) -> _Result:
        return _Result(self._execute_scalar)

    def add(self, _obj: object) -> None:
        pass

    async def commit(self) -> None:
        self.committed = True

    async def refresh(self, _obj: object) -> None:
        pass


def _create_payload(**overrides: object) -> AdminCreate:
    data = {
        "email": "new@example.com",
        "full_name": "New Admin",
        "password": "Secret123!",
        "role_id": uuid.uuid4(),
    }
    data.update(overrides)
    return AdminCreate(**data)  # type: ignore[arg-type]


async def test_create_hashes_password_and_commits() -> None:
    db = _FakeSession(execute_scalar=None, get_map={Role: Role(name="r")})
    data = _create_payload()

    admin = await service.create(db, data)

    assert admin.email == data.email
    assert admin.full_name == data.full_name
    assert admin.role_id == data.role_id
    # password is stored hashed (argon2), never as the plaintext that came in
    assert admin.password != data.password
    assert admin.password.startswith("$argon2")
    assert db.committed is True


async def test_create_raises_on_duplicate_email() -> None:
    # get_by_email finds an existing admin -> conflict, before any role/commit work
    db = _FakeSession(execute_scalar=Admin(email="new@example.com"))
    with pytest.raises(AdminEmailConflict):
        await service.create(db, _create_payload())
    assert db.committed is False


async def test_create_raises_on_invalid_role() -> None:
    # no email conflict, but the referenced role doesn't exist
    db = _FakeSession(execute_scalar=None, get_map={Role: None})
    with pytest.raises(InvalidRole):
        await service.create(db, _create_payload())
    assert db.committed is False


async def test_update_raises_when_admin_missing() -> None:
    db = _FakeSession(get_map={Admin: None})
    with pytest.raises(AdminNotFound):
        await service.update(db, uuid.uuid4(), AdminUpdate(full_name="X"))
    assert db.committed is False


async def test_delete_raises_when_admin_missing() -> None:
    db = _FakeSession(get_map={Admin: None})
    with pytest.raises(AdminNotFound):
        await service.delete(db, uuid.uuid4())
    assert db.committed is False


async def test_set_profile_image_stores_key(monkeypatch: pytest.MonkeyPatch) -> None:
    admin = Admin(email="a@b.com", profile_image_key=None)
    db = _FakeSession(get_map={Admin: admin})

    async def fake_replace_image(old_key, _file, *, prefix):
        assert old_key is None  # admin had no prior image
        assert prefix.startswith("admins/")  # scoped per-admin
        return StoredObject(key="admins/x/avatar/abc.png", url="https://cdn/abc.png")

    monkeypatch.setattr(service.storage, "replace_image", fake_replace_image)

    result = await service.set_profile_image(db, uuid.uuid4(), file=object())  # type: ignore[arg-type]
    assert result.profile_image_key == "admins/x/avatar/abc.png"
    assert db.committed is True


async def test_set_profile_image_raises_when_admin_missing() -> None:
    db = _FakeSession(get_map={Admin: None})
    with pytest.raises(AdminNotFound):
        await service.set_profile_image(db, uuid.uuid4(), file=object())  # type: ignore[arg-type]
    assert db.committed is False


async def test_remove_profile_image_clears_and_deletes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin = Admin(email="a@b.com", profile_image_key="admins/x/avatar/abc.png")
    db = _FakeSession(get_map={Admin: admin})
    deleted: list[str] = []

    async def fake_delete(key: str) -> None:
        deleted.append(key)

    monkeypatch.setattr(service.storage, "delete", fake_delete)

    result = await service.remove_profile_image(db, uuid.uuid4())
    assert result.profile_image_key is None
    assert deleted == ["admins/x/avatar/abc.png"]
    assert db.committed is True


async def test_remove_profile_image_is_noop_when_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin = Admin(email="a@b.com", profile_image_key=None)
    db = _FakeSession(get_map={Admin: admin})
    called: list[str] = []

    async def fake_delete(key: str) -> None:
        called.append(key)

    monkeypatch.setattr(service.storage, "delete", fake_delete)

    result = await service.remove_profile_image(db, uuid.uuid4())
    assert result is admin
    assert called == []  # nothing to delete
    assert db.committed is False  # no state change, no commit


async def test_remove_profile_image_raises_when_admin_missing() -> None:
    db = _FakeSession(get_map={Admin: None})
    with pytest.raises(AdminNotFound):
        await service.remove_profile_image(db, uuid.uuid4())
