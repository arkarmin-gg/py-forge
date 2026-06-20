"""Imports every ORM model module so Base.metadata is fully populated.

Import this (for its side effects) anywhere the full schema is needed: the FastAPI
app, Alembic migrations, and the seed script. The app's routers only reach a subset
of model modules, so without this some cross-domain FKs (e.g. refresh_tokens -> users)
would fail to resolve when mappers configure.
"""

from src.modules.admin_auth import models as _auth  # noqa: F401
from src.modules.admins import models as _admins  # noqa: F401
from src.modules.logs import models as _logs  # noqa: F401
from src.modules.rbac import models as _rbac  # noqa: F401
from src.modules.settings import models as _settings  # noqa: F401
from src.modules.users import models as _users  # noqa: F401
