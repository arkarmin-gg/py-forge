from enum import StrEnum


class RegistrationStage(StrEnum):
    OTP_VERIFIED = "OTP_VERIFIED"
    PASSWORD_SET = "PASSWORD_SET"
    COMPLETED = "COMPLETED"


class LoginProvider(StrEnum):
    SMS = "SMS"
    GOOGLE = "GOOGLE"
    APPLE = "APPLE"
