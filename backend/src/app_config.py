from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class AppConfig(BaseSettings):
    CRAWLER_BASE_URL: str = None
    JSON_FILE_PATH: str = None
    VECTORIZER_FILE_PATH: str = None
    MATRIX_FILE_PATH: str = None
    DOCUMENTS_FILE_PATH: str = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


app_config = AppConfig()