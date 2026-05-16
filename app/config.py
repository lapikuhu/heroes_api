### FastAPI application configuration file

from fastapi import FastAPI
import os
from pathlib import Path
from pydantic_settings import SettingsConfigDict, BaseSettings

env_path = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding="utf-8")

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ADMIN_USERNAME: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    FIXED_ROLES: list[str] = ["admin", "editor", "viewer"]

settings = Settings()

