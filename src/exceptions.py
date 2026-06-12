from fastapi import status


class AppException(Exception):
    """Base for all domain exceptions. Subclasses set status_code/error_code/detail.

    Caught by a single handler in main.py and rendered as an ErrorResponse. Never
    catch bare Exception around route bodies — raise a specific subclass instead.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"
    detail: str = "An unexpected error occurred."

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"
    detail = "Resource not found."


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"
    detail = "Resource already exists."


class UnauthorizedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "unauthorized"
    detail = "Authentication required."


class ForbiddenError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "forbidden"
    detail = "You do not have permission to perform this action."
