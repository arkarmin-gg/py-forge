from enum import StrEnum


class OtpStatus(StrEnum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    EXPIRED = "EXPIRED"
    USED = "USED"


class OtpPurpose(StrEnum):
    TWO_FACTOR = "TWO_FACTOR"
    RESET_PASSWORD = "RESET_PASSWORD"
