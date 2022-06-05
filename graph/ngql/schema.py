from enum import Enum
from typing import Optional

from graph.ngql.connection import run_ngql
from graph.ngql.data_types import string_to_data_type
from graph.ngql.field import NebulaSchemaField


class SubTaskDefinition(object):
    __slots__ = tuple()

    def __str__(self):
        raise NotImplementedError


class TtlDefinition(SubTaskDefinition):
    __slots__ = ('ttl_duration', 'ttl_col')

    def __init__(self, ttl_duration: int, ttl_col: str):
        self.ttl_duration = ttl_duration
        self.ttl_col = ttl_col

    def __str__(self):
        ttl_col = f', TTL_COL = "{self.ttl_col}"' if self.ttl_col else ''
        return f'TTL_DURATION = {self.ttl_duration}{ttl_col}'


class AlterDefinitionType(Enum):
    ADD = 'ADD'
    DROP = 'DROP'
    CHANGE = 'CHANGE'


class SchemaType(Enum):
    TAG = 'TAG'
    EDGE = 'EDGE'


class AlterDefinition(SubTaskDefinition):
    __slots__ = ('alter_definition_type', 'properties', 'prop_names')

    def __init__(
            self, alter_definition_type: AlterDefinitionType, *,
            properties: Optional[list[NebulaSchemaField]] = None, prop_names: list[str] = None
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


def show_schemas(schema: SchemaType) -> list[str]:
    return [i.as_string() for i in run_ngql(f'SHOW {schema.value}S;').column_values('Name')]


def show_tags() -> list[str]:
    return show_schemas(SchemaType.TAG)


def show_edges() -> list[str]:
    return show_schemas(SchemaType.EDGE)


def describe_schema(schema: SchemaType, schema_name: str) -> list[NebulaSchemaField]:
    tag_info = run_ngql(f'DESCRIBE {schema.value} {schema_name};')
    keys = tag_info.keys()
    fields = []
    for row in tag_info.rows():
        dic = {
            keys[i]: str(v.value, encoding='utf-8') if isinstance(v.value, bytes) else v.value
            for i, v in enumerate(row.values)
        }
        fields.append(NebulaSchemaField(
            dic['Field'], string_to_data_type(dic['Type']), nullable=dic['Null'] == 'YES',
            default=dic['Default'], comment=dic['Comment']
        ))
    return fields


def describe_tag(tag_name: str) -> list[NebulaSchemaField]:
    return describe_schema(SchemaType.TAG, tag_name)


def describe_edge(edge_name: str) -> list[NebulaSchemaField]:
    return describe_schema(SchemaType.EDGE, edge_name)


def create_schema_ngql(
        schema: SchemaType,
        schema_name: str, properties: list[NebulaSchemaField], *, if_not_exists: bool = True,
        ttl_definition: Optional[TtlDefinition] = None
) -> str:
    return f'CREATE {schema.value}{" IF NOT EXISTS" if if_not_exists else ""} ' \
           f'{schema_name}({", ".join(str(p) for p in properties)}) {str(ttl_definition) if ttl_definition else ""};'


def create_tag_ngql(
        tag_name: str, properties: list[NebulaSchemaField], *, if_not_exists: bool = True,
        ttl_definition: Optional[TtlDefinition] = None
) -> str:
    return create_schema_ngql(
        SchemaType.TAG, tag_name, properties, if_not_exists=if_not_exists, ttl_definition=ttl_definition
    )


def create_edge_ngql(
        edge_name: str, properties: list[NebulaSchemaField], *, if_not_exists: bool = True,
        ttl_definition: Optional[TtlDefinition] = None
) -> str:
    return create_schema_ngql(
        SchemaType.EDGE, edge_name, properties, if_not_exists=if_not_exists, ttl_definition=ttl_definition
    )


def drop_schema_ngql(schema: SchemaType, schema_name: str, *, if_exists: bool = True) -> str:
    return f'DROP {schema.value}{" IF EXISTS" if if_exists else ""} {schema_name};'


def drop_tag_ngql(tag_name: str, *, if_exists: bool = True) -> str:
    return drop_schema_ngql(SchemaType.TAG, tag_name, if_exists=if_exists)


def drop_edge_ngql(edge_name: str, *, if_exists: bool = True) -> str:
    return drop_schema_ngql(SchemaType.EDGE, edge_name, if_exists=if_exists)


def alter_schema_ngql(
        schema: SchemaType,
        schema_name: str,
        *,
        alter_definitions: Optional[list[AlterDefinition]] = None,
        ttl_definition: Optional[TtlDefinition] = None
) -> str:
    assert alter_definitions or ttl_definition
    return f'ALTER {schema.value} {schema_name} ' \
           f'{", ".join(str(a) for a in alter_definitions) if alter_definitions else ""}' \
           f'{str(ttl_definition) if ttl_definition else ""};'


def alter_tag_ngql(
        tag_name: str,
        *,
        alter_definitions: Optional[list[AlterDefinition]] = None,
        ttl_definition: Optional[TtlDefinition] = None
) -> str:
    return alter_schema_ngql(
        SchemaType.TAG, tag_name, alter_definitions=alter_definitions, ttl_definition=ttl_definition
    )


def alter_edge_ngql(
        edge_name: str,
        *,
        alter_definitions: Optional[list[AlterDefinition]] = None,
        ttl_definition: Optional[TtlDefinition] = None
) -> str:
    return alter_schema_ngql(
        SchemaType.TAG, edge_name, alter_definitions=alter_definitions, ttl_definition=ttl_definition
    )


def delete_tag(tag_names: list[str], vid: str | int):
    run_ngql(f'DELETE TAG {",".join(tag_names)} FROM {vid};')
