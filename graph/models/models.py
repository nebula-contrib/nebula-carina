import json
from collections import OrderedDict
from inspect import isclass
from typing import Union

from nebula3.common.ttypes import Vertex, Tag, Edge
from pydantic import BaseModel
from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass

from graph.models.errors import RecordDoesNotExistError
from graph.models.fields import NebulaFieldInfo
from graph.models.managers import Manager, BaseManager
from graph.ngql.connection import run_ngql
from graph.ngql.schema import TtlDefinition, AlterDefinition, \
    AlterDefinitionType, create_schema_ngql, SchemaType, describe_schema, alter_schema_ngql
from graph.ngql.vertex import insert_vertex_ngql, update_vertex_ngql, upsert_vertex_ngql
from graph.utils.utils import pascal_case_to_snake_case, read_str, classproperty


class NebulaSchemaModel(BaseModel):

    @classmethod
    def _make_db_fields(cls):
        return [
            field.field_info.create_db_field(field_name) for field_name, field in cls.__fields__.items()
            if isinstance(field.field_info, NebulaFieldInfo)
        ]

    @classmethod
    def get_db_field_names(cls) -> list[str]:
        return [
            field_name for field_name, field in cls.__fields__.items() if isinstance(field.field_info, NebulaFieldInfo)
        ]

    def get_db_field_dict(self) -> dict[str, any]:
        return {
            field_name: getattr(self, field_name)
            for field_name in self.get_db_field_names()
        }

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
    @classmethod
    def from_tag(cls, tag: Tag):
        return cls(**{read_str(prop): read_str(value.value) for prop, value in tag.props.items()})


class EdgeTypeModel(NebulaSchemaModel):
    pass


class NebulaRecordModelMetaClass(ModelMetaclass):

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(
            mcs, name, bases, {
                name: field for name, field in namespace.items() if not isinstance(field, Manager)
            }, **kwargs
        )
        setattr(cls, '_managers', {})
        for base in cls.__bases__:
            if 'NebulaRecordModel' in globals() and issubclass(base, NebulaRecordModel):
                cls._managers.update(base._managers)
        for name, field in namespace.items():
            if isinstance(field, Manager):
                cls._managers[name] = field
                setattr(cls, name, classproperty(lambda x: field))
        return cls

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(cls, '_managers'):
            for key, val in cls._managers.items():
                if isinstance(val, Manager):
                    val.register(cls)


class NebulaRecordModel(BaseModel, metaclass=NebulaRecordModelMetaClass):
    @classmethod
    def from_raw(cls, raw_db_item: Vertex | Edge):
        raise NotImplementedError

    objects = BaseManager()


class VertexModel(NebulaRecordModel):

    vid: Union[int, str]

    @classmethod
    def get_tag_name2model(cls) -> dict[str, TagModel]:
        return {
            name: field.type_ for name, field in cls.__fields__.items()
            if isinstance(field, ModelField) and isclass(field.type_) and issubclass(field.type_, TagModel)
        }

    @classmethod
    def from_raw(cls, raw_db_item: Vertex | Edge):
        return cls.from_vertex(raw_db_item)

    @classmethod
    def from_vertex(cls, vertex: Vertex):
        vid = read_str(vertex.vid.value)
        tag_dict = cls.get_tag_name2model()
        return cls(
            vid=vid,
            **{
                read_str(tag.name): tag_dict[read_str(tag.name)].from_tag(tag)
                for tag in vertex.tags if read_str(tag.name) in tag_dict
            }
        )

    def _get_tag_models(self):
        for name, field in self.__class__.__fields__.items():
            if isinstance(field, ModelField) and isclass(field.type_) and issubclass(field.type_, TagModel) \
                    and getattr(self, name, None):
                yield name, field.type_

    def upsert(self):
        for name, tag_model in self._get_tag_models():
            run_ngql(upsert_vertex_ngql(tag_model.db_name(), self.vid, getattr(self, name).get_db_field_dict()))

    def save(self, *, if_not_exists: bool = False):
        #   并发不安全，如果需要并发安全，需要考虑upsert
        try:
            self.objects.get(self.vid)
            for name, tag_model in self._get_tag_models():
                run_ngql(update_vertex_ngql(tag_model.db_name(), self.vid, getattr(self, name).get_db_field_dict()))
        except RecordDoesNotExistError:
            tag_props = OrderedDict()
            data = []
            for name, tag_model in self._get_tag_models():
                tag_props[tag_model.db_name()] = tag_model.get_db_field_names()
                data.extend(
                    [getattr(getattr(self, name), field_name) for field_name in tag_props[tag_model.db_name()]]
                )
            ngql = insert_vertex_ngql(tag_props, {json.dumps(self.vid): data}, if_not_exists=if_not_exists)
            run_ngql(ngql)


class EdgeModel(NebulaRecordModel):
    vid: Union[int, str]

    @classmethod
    def from_raw(cls, raw_db_item: Vertex | Edge):
        raise NotImplementedError
