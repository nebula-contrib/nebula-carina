from nebula_carina.ngql.connection.connection import run_ngql, LocalSession
from enum import Enum
from nebula_carina.utils.utils import read_str


class VidTypeEnum(Enum):
    INT64 = 'INT64'
    FIXED_STRING = 'FIXED_STRING(%s)'


def show_spaces() -> list[str]:
    return LocalSession().raw_show_spaces()


def make_vid_desc_string(vid_desc: VidTypeEnum | tuple[VidTypeEnum, int] | str):
    if isinstance(vid_desc, str):
        return vid_desc
    elif isinstance(vid_desc, tuple):
        assert vid_desc[0] == VidTypeEnum.FIXED_STRING, 'only fixed string vid should be processed as tuple'
        assert isinstance(vid_desc[1], int) and vid_desc[1] > 0, 'fixed string vid must have a positive length'
        vid_desc = vid_desc[0].value % vid_desc[1]
    else:
        assert vid_desc == VidTypeEnum.INT64
        vid_desc = vid_desc.value
    return vid_desc


def create_space(
        name: str, vid_desc: VidTypeEnum | tuple[VidTypeEnum, int] | str,
        *,
        if_not_exists: bool = True, partition_num: int = 100, replica_factor: int = 1, comment: str = None
):
    additional_descriptions = {
        'vid_type': make_vid_desc_string(vid_desc),
        'partition_num': partition_num,
        'replica_factor': replica_factor,
    }
    if comment:
        comment = f' COMMENT="{comment}"'
    run_ngql(
        f'CREATE SPACE {"IF NOT EXISTS " if if_not_exists else ""}{name} '
        f'({", ".join("%s=%s" % (k, v) for k, v in additional_descriptions.items())}){comment or ""};',
        is_spacial_operation=True
    )


def use_space(name):
    return LocalSession().raw_use_space(name)


def clear_space(name: str, if_exists: bool = True):
    run_ngql(f'CLEAR SPACE {"IF EXISTS " if if_exists else ""}{name};', is_spacial_operation=True)


def drop_space(name: str, if_exists: bool = True):
    run_ngql(f'DROP SPACE {"IF EXISTS " if if_exists else ""}{name};', is_spacial_operation=True)


def describe_space(name: str) -> dict[str, any]:
    result = run_ngql(f'DESCRIBE SPACE {name};', is_spacial_operation=True)
    return {k: read_str(v.value) for k, v in zip(result.keys(), result.rows()[0].values)}
