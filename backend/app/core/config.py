from pydantic_settings import BaseSettings
from typing import Optional
import os
from urllib.parse import quote_plus


class Settings(BaseSettings):
    model_config = {
        "protected_namespaces": (),
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    # Database
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = "root"
    db_name: str = "sysmldocgen"

    # JWT（概要：access 约 2 小时 + refresh）
    secret_key: str = "sysmldocgen-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    refresh_token_expire_days: int = 7

    # Storage
    upload_dir: str = "./storage"
    storage_model_dir: str = "./storage/models"
    template_dir: str = "./storage/templates"
    document_dir: str = "./storage/documents"
    log_dir: str = "./logs"

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    @property
    def database_url(self) -> str:
        password = quote_plus(self.db_password)
        return f"mysql+pymysql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"


settings = Settings()
