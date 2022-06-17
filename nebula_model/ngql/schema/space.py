from nebula_model.ngql.connection.connection import run_ngql
from enum import Enum


class VidTypeEnum(Enum):
    INT64 = 'INT64'
    FIXED_STRING = 'FIXED_STRING(%s)'


def show_spaces() -> list[str]:
    return [i.as_string() for i in run_ngql('SHOW SPACES;').column_values('Name')]


def create_space(name: str, vid_desc: VidTypeEnum | tuple[VidTypeEnum, int], if_not_exists: bool = True):
    if isinstance(vid_desc, tuple):
        assert vid_desc[0] == VidTypeEnum.FIXED_STRING, 'only fixed string vid should be processed as tuple'
        assert isinstance(vid_desc[1], int) and vid_desc[1] > 0, 'fixed string vid must have a positive length'
        vid_desc = vid_desc[0].value % vid_desc[1]
    else:
        assert vid_desc == VidTypeEnum.INT64
        vid_desc = vid_desc.value
    run_ngql(f'CREATE SPACE {"IF NOT EXISTS " if if_not_exists else ""}{name} (vid_type={vid_desc});')


def use_space(name):
    run_ngql(f'USE {name};')


def clear_space(name: str, if_exists: bool = True):
    run_ngql(f'CLEAR SPACE {"IF EXISTS " if if_exists else ""}{name};')


def drop_space(name: str, if_exists: bool = True):
    run_ngql(f'DROP SPACE {"IF EXISTS " if if_exists else ""}{name};')


def describe_space(name: str):
    run_ngql(f'DESCRIBE SPACE {name};')
