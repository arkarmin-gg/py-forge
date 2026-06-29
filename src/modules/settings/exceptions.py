from src.exceptions import NotFoundError


class SettingNotFound(NotFoundError):
    error_code = "setting_not_found"
    detail = "Setting not found."
