"""Application configuration."""

from pydantic import computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Mini Agent Platform"

    # Logger
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # MongoDB setup — FastAPI connects as app_user only
    MONGODB_APP_USER: str = "app_user"
    MONGODB_APP_PASSWORD: str
    MONGODB_DB: str
    MONGODB_HOST: str

    @computed_field
    @property
    def MONGODB_URI(self) -> str:
        url = MultiHostUrl.build(
            scheme="mongodb",
            username=self.MONGODB_APP_USER,
            password=self.MONGODB_APP_PASSWORD,
            host=self.MONGODB_HOST,
            path=self.MONGODB_DB,
            query=f"authSource={self.MONGODB_DB}"
        )
        return str(url)

    MAX_EXECUTION_STEPS: int
    TENANT_API_KEYS: dict[str, str]

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="ignore",
    )

settings = Settings()