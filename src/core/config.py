from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ASYNC_DATABASE_URL: str
    SYNC_DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAIL_FROM: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
