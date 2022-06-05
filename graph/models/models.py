from enum import Enum
from typing import Union

from pydantic import BaseModel

from graph.models.fields import NebulaFieldInfo
from graph.ngql.schema import TtlDefinition, AlterDefinition, \
    AlterDefinitionType, create_schema_ngql, SchemaType, describe_schema, alter_schema_ngql
from graph.utils.utils import pascal_case_to_snake_case


class NebulaSchemaModel(BaseModel):

    @classmethod
    def _make_db_fields(cls):
        return [
            field.field_info.create_db_field(field_name) for field_name, field in cls.__fields__.items()
            if isinstance(field.field_info, NebulaFieldInfo)
        ]

    @classmethod
    def db_name(cls):
        return pascal_case_to_snake_case(cls.__name__)

    @classmethod
    def get_schema_type(cls) -> SchemaType:
        schema_type = None
        if issubclass(cls, TagModel):
            schema_type = SchemaType.TAG
        elif issubclass(cls, EdgeTypeModel):
            schema_type = SchemaType.EDGE
        assert schema_type
        return schema_type

    @classmethod
    def create_schema_ngql(cls):
        db_fields = cls._make_db_fields()
        meta_cls = getattr(cls, 'Meta', None)
        return create_schema_ngql(
            cls.get_schema_type(),
            cls.db_name(), db_fields,
            ttl_definition=TtlDefinition(meta_cls.ttl_duration, meta_cls.ttl_col)
            if meta_cls and getattr(meta_cls, 'ttl_duration', None) else None
        )

    @classmethod
    def alter_schema_ngql(cls):
        # TODO ttl
        from_dict = {db_field.prop_name: db_field for db_field in describe_schema(cls.get_schema_type(), cls.db_name())}
        to_dict = {db_field.prop_name: db_field for db_field in cls._make_db_fields()}
        adds, drop_names, changes = [], [], []
        for name, db_field in to_dict.items():
            if name not in from_dict:
                adds.append(db_field)
            elif db_field != from_dict[name]:
                changes.append(db_field)
        for name, db_field in from_dict.items():
            if name not in to_dict:
                drop_names.append(name)
        if adds or drop_names or changes:
            alter_definitions = []
            if adds:
                alter_definitions.append(AlterDefinition(AlterDefinitionType.ADD, properties=adds))
            if changes:
                alter_definitions.append(AlterDefinition(AlterDefinitionType.CHANGE, properties=changes))
            if drop_names:
                alter_definitions.append(AlterDefinition(AlterDefinitionType.DROP, prop_names=drop_names))
            return alter_schema_ngql(cls.get_schema_type(), cls.db_name(), alter_definitions=alter_definitions)
        return None


class TagModel(NebulaSchemaModel):
    pass


class EdgeTypeModel(NebulaSchemaModel):
    pass


class NebulaRecordModel(BaseModel):
    pass


class Vertex(NebulaRecordModel):
    vid: Union[int, str]

    def save(self, tags: list[TagModel]):
        pass


class Edge(NebulaRecordModel):
    pass
