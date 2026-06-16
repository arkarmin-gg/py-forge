from fastapi import status

from src.exceptions import AppException, ConflictError, NotFoundError


class AdminNotFound(NotFoundError):
    error_code = "admin_not_found"
    detail = "Admin not found."


class AdminEmailConflict(ConflictError):
    error_code = "admin_email_conflict"
    detail = "An admin with this email already exists."


class InvalidRole(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    error_code = "invalid_role"
    detail = "The specified role does not exist."
