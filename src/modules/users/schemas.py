import uuid
from datetime import datetime

from src.modules.users.constants import LoginProvider, RegistrationStage
from src.schemas import ResponseSchema


class UserRead(ResponseSchema):
    id: uuid.UUID
    phone: str
    email: str | None
    full_name: str | None
    is_banned: bool
    registration_stage: RegistrationStage
    login_provider: LoginProvider | None
    created_at: datetime
