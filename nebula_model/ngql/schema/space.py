from nebula_model.ngql.connection.connection import run_ngql
from enum import Enum


class VidTypeEnum(Enum):
    INT64 = 'INT64'
    FIXED_STRING_8 = 'FIXED_STRING(8)'
    FIXED_STRING_16 = 'FIXED_STRING(16)'
    FIXED_STRING_32 = 'FIXED_STRING(32)'


def show_spaces() -> list[str]:
    return [i.as_string() for i in run_ngql('SHOW SPACES;').column_values('Name')]


def create_space(name: str, vid_type: VidTypeEnum):
    run_ngql(f'CREATE SPACE IF NOT EXISTS {name} (vid_type={vid_type.value});')


def use_space(name):
    run_ngql(f'USE {name};')
