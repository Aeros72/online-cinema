from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ASYNC_DATABASE_URL: str
    SYNC_DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
