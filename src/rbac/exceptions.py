from fastapi import status

from src.exceptions import AppException


class PermissionDenied(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "permission_denied"
    detail = "You do not have permission to perform this action."
