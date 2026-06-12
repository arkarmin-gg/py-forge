from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base for response models read off ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Consistent error envelope returned by the AppException handler."""

    error_code: str
    detail: str
