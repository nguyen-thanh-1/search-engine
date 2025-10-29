from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

app_config = AppConfig()
