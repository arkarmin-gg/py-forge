"""Imports every ORM model module so Base.metadata is fully populated.

Import this (for its side effects) anywhere the full schema is needed: the FastAPI
app, Alembic migrations, and the seed script. The app's routers only reach a subset
of model modules, so without this some cross-domain FKs (e.g. refresh_tokens -> users)
would fail to resolve when mappers configure.
"""

from src.admins import models as _admins  # noqa: F401
from src.auth import models as _auth  # noqa: F401
from src.logs import models as _logs  # noqa: F401
from src.rbac import models as _rbac  # noqa: F401
from src.settings import models as _settings  # noqa: F401
from src.users import models as _users  # noqa: F401
