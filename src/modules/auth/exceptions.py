from fastapi import status

from src.exceptions import AppException


class InvalidCredentials(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "invalid_credentials"
    detail = "Incorrect email or password."


class InvalidToken(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "invalid_token"
    detail = "Token is missing, invalid, or expired."


class InactiveAdmin(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "inactive_admin"
    detail = "This admin account is banned."


class InvalidCurrentPassword(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "invalid_current_password"
    detail = "Current password is incorrect."
