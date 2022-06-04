from enum import Enum

from pydantic import BaseModel

from graph.models.fields import NebulaFieldInfo
from graph.ngql.field import NebulaDatabaseField
from graph.ngql.tag import create_tag_ngql, TtlDefinition, show_tags, describe_tag
from graph.utils.utils import pascal_case_to_snake_case


class NebulaModel(BaseModel):

    @classmethod
    def _construct(cls):
        raise NotImplementedError


class TagModel(NebulaModel):
    @classmethod
    def _make_db_fields(cls):
        return [
            field.field_info.create_db_field(field_name) for field_name, field in cls.__fields__.items()
            if isinstance(field.field_info, NebulaFieldInfo)
        ]

    @classmethod
    def _construct_tag(cls):
        db_fields = cls._make_db_fields()
        tag_name = pascal_case_to_snake_case(cls.__name__)
        meta_cls = getattr(cls, 'Meta')
        return create_tag_ngql(
            tag_name, db_fields,
            ttl_definition=TtlDefinition(meta_cls.ttl_duration, meta_cls.ttl_col)
            if meta_cls and getattr(meta_cls, 'ttl_duration') else None
        )

    @classmethod
    def _compare_and_alter(cls):
        pass

    @classmethod
    def analyse_structure(cls):
        tag_name = pascal_case_to_snake_case(cls.__name__)
        tag_info = describe_tag(tag_name)
        return tag_info


class EdgeTypeModel(NebulaModel):

    @classmethod
    def _construct(cls):
        pass
