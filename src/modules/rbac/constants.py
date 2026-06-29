from enum import StrEnum


class ActionType(StrEnum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


SUPERADMIN_ROLE_NAME = "superadmin"
