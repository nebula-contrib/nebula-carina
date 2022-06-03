from typing import Optional

from graph.ngql.connection import run_ngql
from graph.ngql.field import NebulaDatabaseField


def show_tags() -> list[str]:
    return run_ngql('SHOW TAGS;').column_values('Name')


def describe_tag(tag_name: str):
    result = run_ngql(f'DESCRIBE TAG {tag_name};')
    return result


def create_tag(
        tag_name: str, properties: list[NebulaDatabaseField], if_not_exists: bool = True,
        ttl_duration: int = 0, ttl_col: Optional[str] = None,
):
    run_ngql(f'CREATE TAG{" IF NOT EXISTS" if if_not_exists else ""} '
             f'{tag_name}({", ".join(str(p) for p in properties)})'
             f'{" TTL_DURATION" if ttl_duration else ""}{" TTL_COL" if ttl_col else ""}')


def drop_tag(tag_name, if_exists=True):
    run_ngql(f'DROP TAG{" IF EXISTS" if if_exists else ""} {tag_name}')
