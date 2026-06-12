import uuid
from datetime import datetime

from src.schemas import BaseSchema
from src.users.constants import LoginProvider, RegistrationStage


class UserRead(BaseSchema):
    """Stub response model. The users domain is modeled but not yet wired to routes."""

    id: uuid.UUID
    phone: str
    email: str | None
    full_name: str | None
    is_banned: bool
    registration_stage: RegistrationStage
    login_provider: LoginProvider | None
    created_at: datetime
