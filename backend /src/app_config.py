from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class AppConfig(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    CRAWLER_BASE_URL: str = None
    JSON_FILE: str = None
    DATA_DIR: str = None
    VECTORIZER_FILE: str = None
    MATRIX_FILE: str = None
    DOCUMENTS_FILE: str = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


app_config = AppConfig()