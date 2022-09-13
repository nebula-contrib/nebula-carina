from typing import Set, Optional, Union
import typing
from pydantic import BaseSettings


try:
    # for django
    from django.conf import settings

    class DjangoCarinaDatabaseSettings(object):

        max_connection_pool_size: int = 10
        servers: Set[str] = set()
        user_name: str
        password: str
        default_space: str = 'main'
        auto_create_default_space_with_vid_desc: Optional[str]

        model_paths: Set[str] = set()
        timezone_name: str = 'UTC'

        @staticmethod
        def is_optional(tp):
            return typing.get_origin(tp) is Union and type(None) in typing.get_args(tp)

        def __init__(self, **kwargs):
            for key, type_ in DjangoCarinaDatabaseSettings.__dict__['__annotations__'].items():
                if not self.is_optional(type_) and not hasattr(DjangoCarinaDatabaseSettings, key):
                    assert key in kwargs, f'Setting {key} is required but not provided in CARINA_SETTINGS.'
                key in kwargs and setattr(self, key, kwargs[key])

    database_settings = DjangoCarinaDatabaseSettings(**settings.CARINA_SETTINGS)
except ModuleNotFoundError:
    class DatabaseSettings(BaseSettings):

        max_connection_pool_size: int = 10
        servers: Set[str] = set()
        user_name: str
        password: str
        default_space: str = 'main'
        auto_create_default_space_with_vid_desc: Optional[str]

        model_paths: Set[str] = set()
        timezone_name: str = 'UTC'

        class Config:
            env_prefix = 'nebula_'


    database_settings = DatabaseSettings()
