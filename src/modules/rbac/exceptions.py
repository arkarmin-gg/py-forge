from fastapi import status

from src.exceptions import AppException, ConflictError, NotFoundError


class PermissionDenied(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "permission_denied"
    detail = "You do not have permission to perform this action."


class RoleNotFound(NotFoundError):
    error_code = "role_not_found"
    detail = "Role not found."


class RoleNameConflict(ConflictError):
    error_code = "role_name_conflict"
    detail = "A role with this name already exists."


class ProtectedRole(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "protected_role"
    detail = "The superadmin role cannot be modified."


class RoleAssigned(ConflictError):
    error_code = "role_assigned"
    detail = "This role is assigned to one or more admins."


class InvalidPermission(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    error_code = "invalid_permission"
    detail = "One or more permissions do not exist."
