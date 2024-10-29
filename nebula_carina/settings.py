from typing import Set, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    max_connection_pool_size: int = 10
    servers: Set[str] = set()
    user_name: str
    password: str
    default_space: str = "main"
    auto_create_default_space_with_vid_desc: Optional[str]

    timezone_name: str = "UTC"
    model_config = SettingsConfigDict(
        env_prefix="nebula_", env_file=".env", extra="ignore"
    )


database_settings = DatabaseSettings()
