from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_", env_file=".env", extra="ignore")

    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_ACCESS_EXP_MINUTES: int = 15
    REFRESH_TOKEN_EXP_DAYS: int = 30


auth_settings = AuthConfig()  # type: ignore[call-arg]
