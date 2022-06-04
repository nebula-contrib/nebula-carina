from enum import Enum
from typing import Optional

from graph.ngql.connection import run_ngql
from graph.ngql.field import NebulaDatabaseField


class SubTaskDefinition(object):
    __slots__ = tuple()

    def __str__(self):
        raise NotImplementedError


def show_tags() -> list[str]:
    return run_ngql('SHOW TAGS;').column_values('Name')


def describe_tag(tag_name: str):
    result = run_ngql(f'DESCRIBE TAG {tag_name};')
    return result


class TtlDefinition(SubTaskDefinition):
    __slots__ = ('ttl_duration', 'ttl_col')

    def __init__(self, ttl_duration: int, ttl_col: Optional[str]):
        self.ttl_duration = ttl_duration
        self.ttl_col = ttl_col

    def __str__(self):
        return f'TTL_DURATION = {self.ttl_duration}{f", TTL_COL = {self.ttl_col}" if self.ttl_col else ""}'


def create_tag(
        tag_name: str, properties: list[NebulaDatabaseField], if_not_exists: bool = True,
        ttl_definition: Optional[TtlDefinition] = None
):
    run_ngql(
        f'CREATE TAG{" IF NOT EXISTS" if if_not_exists else ""} '
        f'{tag_name}({", ".join(str(p) for p in properties)}) {str(ttl_definition) if ttl_definition else ""};'
    )


def drop_tag(tag_name: str, if_exists: bool = True):
    run_ngql(f'DROP TAG{" IF EXISTS" if if_exists else ""} {tag_name};')


class AlterDefinitionType(Enum):
    ADD = 'ADD'
    DROP = 'DROP'
    CHANGE = 'CHANGE'


class AlterDefinition(SubTaskDefinition):
    __slots__ = ('alter_definition_type', 'properties', 'prop_names')

    def __init__(
            self, alter_definition_type: AlterDefinitionType, *,
            properties: Optional[list[NebulaDatabaseField]] = None, prop_names: list[str] = None
    ):
        self.alter_definition_type = alter_definition_type
        if self.alter_definition_type == AlterDefinitionType.DROP:
            assert prop_names
            self.prop_names = prop_names
        else:
            assert properties
            self.properties = properties

    def __str__(self):
        if self.alter_definition_type == AlterDefinitionType.DROP:
            return f'{self.alter_definition_type.value} ({",".join(self.prop_names)})'
        return f'{self.alter_definition_type.value} ({", ".join(str(p) for p in self.properties)})'


def alter_tag(
        tag_name: str,
        alter_definitions: Optional[list[AlterDefinition]] = None,
        ttl_definition: Optional[TtlDefinition] = None
):
    assert alter_definitions or ttl_definition
    run_ngql(
        f'ALTER TAG {tag_name} {", ".join(str(a) for a in alter_definitions) if alter_definitions else ""}'
        f'{str(ttl_definition) if ttl_definition else ""};'
    )


def delete_tag(tag_names: list[str], vid: str | int):
    run_ngql(f'DELETE TAG {",".join(tag_names)} FROM {vid};')
