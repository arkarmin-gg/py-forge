from pydantic import Field

from src.schemas import RequestSchema


class TokenResponse(RequestSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(RequestSchema):
    refresh_token: str


class ChangePasswordRequest(RequestSchema):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
