from collections import OrderedDict
from copy import deepcopy
from functools import partial
from inspect import isclass
from typing import Iterable

from nebula3.common.ttypes import Vertex, Tag, Edge
from pydantic import BaseModel
from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass

from nebula_carina.models.abstract import NebulaAdaptor
from nebula_carina.models.errors import VertexDoesNotExistError, EdgeDoesNotExistError, DuplicateEdgeTypeNameError
from nebula_carina.models.fields import NebulaFieldInfo
from nebula_carina.models.managers import Manager, BaseVertexManager, BaseEdgeManager
from nebula_carina.models.model_builder import ModelBuilder
from nebula_carina.ngql.connection.connection import run_ngql
from nebula_carina.ngql.query.conditions import Q
from nebula_carina.ngql.record.edge import update_edge_ngql, insert_edge_ngql, upsert_edge_ngql
from nebula_carina.ngql.schema.data_types import ttype2python_value
from nebula_carina.ngql.schema.schema import Ttl, Alter, \
    create_schema_ngql, describe_schema, alter_schema_ngql
from nebula_carina.ngql.statements.clauses import Limit
from nebula_carina.ngql.statements.edge import EdgeDefinition, EdgeValue
from nebula_carina.ngql.statements.schema import AlterType, SchemaType
from nebula_carina.ngql.record.vertex import insert_vertex_ngql, update_vertex_ngql, upsert_vertex_ngql
from nebula_carina.utils.utils import pascal_case_to_snake_case, read_str, classproperty


_edge_type_model_factory = {}


class NebulaSchemaModelMetaClass(ModelMetaclass):

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'EdgeTypeModel' in globals() and issubclass(cls, EdgeTypeModel):
            db_name = cls.db_name()
            if db_name in _edge_type_model_factory:
                raise DuplicateEdgeTypeNameError(cls.__name__)
            _edge_type_model_factory[db_name] = cls


class NebulaSchemaModel(BaseModel, metaclass=NebulaSchemaModelMetaClass):

    @classmethod
    def _create_db_fields(cls):
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
            field_name: field.field_info.data_type.value2db_str(getattr(self, field_name))
            for field_name, field in self.__class__.__fields__.items() if isinstance(field.field_info, NebulaFieldInfo)
        }

    def get_db_field_value(self, field_name) -> str:
        return self.__class__.__fields__[field_name].field_info.data_type.value2db_str(getattr(self, field_name))

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
        db_fields = cls._create_db_fields()
        meta_cls = getattr(cls, 'Meta', None)
        return create_schema_ngql(
            cls.get_schema_type(),
            cls.db_name(), db_fields,
            ttl_definition=Ttl(meta_cls.ttl_duration, meta_cls.ttl_col)
            if meta_cls and getattr(meta_cls, 'ttl_duration', None) else None
        )

    @classmethod
    def alter_schema_ngql(cls):
        # TODO ttl where to get the ttl info?
        from_dict = {db_field.prop_name: db_field for db_field in describe_schema(cls.get_schema_type(), cls.db_name())}
        to_dict = {db_field.prop_name: db_field for db_field in cls._create_db_fields()}
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
                alter_definitions.append(Alter(AlterType.ADD, properties=adds))
            if changes:
                alter_definitions.append(Alter(AlterType.CHANGE, properties=changes))
            if drop_names:
                alter_definitions.append(Alter(AlterType.DROP, prop_names=drop_names))
            return alter_schema_ngql(
                cls.get_schema_type(), cls.db_name(),
                alter_definitions=alter_definitions,
            )
        return None


class TagModel(NebulaSchemaModel):
    @classmethod
    def from_tag(cls, tag: Tag):
        return cls(**{read_str(prop): ttype2python_value(value.value) for prop, value in tag.props.items()})

    @classmethod
    def get_db_name_pattern(cls) -> str:
        """
        return the db names pattern e.g.  ":figure:source"
        """
        if cls is TagModel:
            return ''
        return ':' + cls.db_name()


class EdgeTypeModel(NebulaSchemaModel):
    @classmethod
    def from_props(cls, props: dict[str, any]):
        return cls(**{read_str(prop): read_str(value.value) for prop, value in props.items()})

    @classmethod
    def get_db_name_pattern(cls) -> str:
        """
        return the db names pattern e.g.  ":figure:source"
        """
        if cls is EdgeTypeModel:
            return ''
        return ':' + cls.db_name()


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
                cls._managers.update(deepcopy(base._managers))
        for name, field in namespace.items():
            if isinstance(field, Manager):
                field = deepcopy(field)
                cls._managers[name] = field
                setattr(cls, name, classproperty(partial(lambda x, f: f, f=field)))
        return cls

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(cls, '_managers'):
            for key, val in cls._managers.items():
                if isinstance(val, Manager):
                    setattr(cls, key, val)
                    val.register(cls)


class NebulaRecordModel(BaseModel, NebulaAdaptor, metaclass=NebulaRecordModelMetaClass):
    objects = BaseVertexManager()


class VertexModel(NebulaRecordModel):

    vid: int | str
    objects = BaseVertexManager()

    @classmethod
    def iterate_tag_models(cls) -> tuple[str, TagModel]:
        """
        return the iterator of tuple[name, tag model] of this class
        """
        for name, field in cls.__fields__.items():
            if isinstance(field, ModelField) and isclass(field.type_) and issubclass(field.type_, TagModel):
                yield name, field.type_, field.required

    @classmethod
    def get_tag_name2model(cls) -> dict[str, TagModel]:
        """
        get the tag name towards the model
        note that the tag name might be different from the tag's db name
        e.g. {'figure': <class 'example.models.Figure'>, 'source1': <class 'example.models.Source'>}
        """
        return {
            name: tag_model for name, tag_model, _ in cls.iterate_tag_models()
        }

    @classmethod
    def from_nebula_db_cls(cls, raw_db_item: Vertex | Edge):
        """
        convert nebula python vertex to VertexModel
        """
        return cls.from_vertex(raw_db_item)

    @classmethod
    def from_vertex(cls, vertex: Vertex):
        """
        convert nebula python vertex to VertexModel
        """
        vid = read_str(vertex.vid.value)
        tag_dict = cls.get_tag_name2model()
        return cls(
            vid=vid,
            **{
                read_str(tag.name): tag_dict[read_str(tag.name)].from_tag(tag)
                for tag in vertex.tags if read_str(tag.name) in tag_dict
            }
        )

    @classmethod
    def get_db_name_pattern(cls) -> str:
        """
        return the db names pattern e.g.  ":figure:source"
        """
        required_only = True  # FIXME: maybe we will allow non-required feature in future
        return ''.join(
            tag_model.get_db_name_pattern() for _, tag_model, required in cls.iterate_tag_models()
            if not required_only or required
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
        except VertexDoesNotExistError:
            tag_props = OrderedDict()
            data = []
            for name, tag_model in self._get_tag_models():
                tag_props[tag_model.db_name()] = tag_model.get_db_field_names()
                data.extend(
                    [
                        getattr(self, name).get_db_field_value(field_name)
                        for field_name in tag_props[tag_model.db_name()]
                    ]
                )
            ngql = insert_vertex_ngql(tag_props, {self.vid: data}, if_not_exists=if_not_exists)
            run_ngql(ngql)

    def get_out_edges(self, edge_type: EdgeTypeModel = None, *, limit: Limit = None):
        return EdgeModel.objects.find_by_source(self.vid, edge_type, limit=limit)

    def get_out_edge_and_destinations(self, edge_type, dst_vertex_model, *, limit: Limit = None) \
            -> Iterable[dict[str, NebulaAdaptor]]:
        if edge_type is None:
            edge_type = EdgeTypeModel
        return (
            {'edge': r['e'], 'dst': r['v2']} for r in ModelBuilder.match(
                f'(v1)-[e{edge_type.get_db_name_pattern()}]->(v2{dst_vertex_model.get_db_name_pattern()})',
                {'e': EdgeModel, 'v2': dst_vertex_model},
                condition=Q(v1__id=self.vid), limit=limit
            )
        )

    def get_destinations(self, edge_type, dst_vertex_model, *, distinct=False, limit: Limit = None):
        return dst_vertex_model.objects.find_destinations(self.vid, edge_type, distinct=distinct, limit=limit)

    def get_reverse_edges(self, edge_type: EdgeTypeModel = None, *, limit: Limit = None):
        return EdgeModel.objects.find_by_destination(self.vid, edge_type, limit=limit)

    def get_reverse_edge_and_sources(self, edge_type, src_vertex_model, *, limit: Limit = None) \
            -> Iterable[dict[str, NebulaAdaptor]]:
        if edge_type is None:
            edge_type = EdgeTypeModel
        return (
            {'edge': r['e'], 'src': r['v1']} for r in ModelBuilder.match(
                f'(v1{src_vertex_model.get_db_name_pattern()})-[e{edge_type.get_db_name_pattern()}]->(v2)',
                {'e': EdgeModel, 'v1': src_vertex_model},
                condition=Q(v2__id=self.vid), limit=limit
            )
        )

    def get_sources(self, edge_type, src_vertex_model, *, distinct=False, limit: Limit = None):
        return src_vertex_model.objects.find_sources(self.vid, edge_type, distinct=distinct, limit=limit)


class EdgeModel(NebulaRecordModel):
    src_vid: int | str
    dst_vid: int | str
    ranking: int = 0
    edge_type_name: str | None  # for view only
    edge_type: EdgeTypeModel  # only one edge type
    objects = BaseEdgeManager()

    def get_edge_type_and_model(self):
        return self.edge_type.db_name(), self.edge_type.__class__

    @classmethod
    def from_nebula_db_cls(cls, raw_db_item: Vertex | Edge):
        return cls.from_edge(raw_db_item)

    @classmethod
    def from_edge(cls, edge: Edge):
        src = read_str(edge.src.value)
        dst = read_str(edge.dst.value)
        edge_type_name = read_str(edge.name)
        ranking = edge.ranking
        # need a dict to hold all the edge types
        edge_type = _edge_type_model_factory[edge_type_name]
        return cls(
            src_vid=src,
            dst_vid=dst,
            ranking=ranking,
            edge_type_name=edge_type_name,
            edge_type=edge_type.from_props(edge.props),
        )

    def upsert(self):
        _, edge_model = self.get_edge_type_and_model()
        run_ngql(upsert_edge_ngql(
            edge_model.db_name(), EdgeDefinition(self.src_vid, self.dst_vid, self.ranking),
            self.edge_type.get_db_field_dict()
        ))

    def save(self, *, if_not_exists: bool = False):
        #   并发不安全，如果需要并发安全，需要考虑upsert
        _, edge_type_model = self.get_edge_type_and_model()
        try:
            self.objects.get(self.src_vid, self.dst_vid, self.edge_type.__class__)

            run_ngql(update_edge_ngql(
                edge_type_model.db_name(),
                EdgeDefinition(self.src_vid, self.dst_vid, self.ranking),
                self.edge_type.get_db_field_dict()
            ))
        except EdgeDoesNotExistError:
            db_field_names = edge_type_model.get_db_field_names()
            ngql = insert_edge_ngql(
                edge_type_model.db_name(), db_field_names,
                [EdgeValue(
                    self.src_vid, self.dst_vid,
                    [self.edge_type.get_db_field_value(field_name) for field_name in db_field_names],
                    ranking=self.ranking
                )],
                if_not_exists=if_not_exists
            )
            run_ngql(ngql)
