from typing import Set

from pydantic import BaseSettings


class DatabaseSettings(BaseSettings):
    max_connection_pool_size: int = 10
    servers: Set[str] = set()
    user_name: str
    password: str
    default_space: str = 'main'

    class Config:
        env_prefix = 'nebula_'


database_settings = DatabaseSettings()
