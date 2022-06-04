from enum import Enum

from pydantic import BaseModel

from graph.models.fields import NebulaFieldInfo
from graph.ngql.tag import create_tag_ngql, TtlDefinition, describe_tag, alter_tag, alter_tag_ngql, AlterDefinition, \
    AlterDefinitionType
from graph.utils.utils import pascal_case_to_snake_case


class NebulaModel(BaseModel):

    @classmethod
    def _make_db_fields(cls):
        return [
            field.field_info.create_db_field(field_name) for field_name, field in cls.__fields__.items()
            if isinstance(field.field_info, NebulaFieldInfo)
        ]

    @classmethod
    def _create_tag(cls):
        raise NotImplementedError

    @classmethod
    def _alter_tag(cls):
        raise NotImplementedError


class TagModel(NebulaModel):
    @classmethod
    def _create_tag(cls):
        db_fields = cls._make_db_fields()
        tag_name = pascal_case_to_snake_case(cls.__name__)
        meta_cls = getattr(cls, 'Meta')
        return create_tag_ngql(
            tag_name, db_fields,
            ttl_definition=TtlDefinition(meta_cls.ttl_duration, meta_cls.ttl_col)
            if meta_cls and getattr(meta_cls, 'ttl_duration') else None
        )

    @classmethod
    def _alter_tag(cls):
        # TODO ttl
        tag_name = pascal_case_to_snake_case(cls.__name__)
        from_dict = {db_field.prop_name: db_field for db_field in describe_tag(tag_name)}
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
            return alter_tag_ngql(tag_name, alter_definitions=alter_definitions)
        return None


class EdgeTypeModel(NebulaModel):
    @classmethod
    def _create_tag(cls):
        raise NotImplementedError

    @classmethod
    def _alter_tag(cls):
        raise NotImplementedError
