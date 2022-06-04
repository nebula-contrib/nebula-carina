from enum import Enum

from pydantic import BaseModel

from graph.models.fields import NebulaFieldInfo


class NebulaModelType(Enum):
    UNDEFINED = 'undefined'
    TAG = 'tag'
    EDGE_TYPE = 'edge_type'


class NebulaModel(BaseModel):
    model_type = NebulaModelType.UNDEFINED

    @classmethod
    def _construct(cls):
        raise NotImplementedError


class TagModel(NebulaModel):
    model_type = NebulaModelType.TAG

    @classmethod
    def _construct(cls):
        for field_name, field in cls.__fields__.items():
            if not isinstance(field.field_info, NebulaFieldInfo):
                continue


class EdgeTypeModel(NebulaModel):
    model_type = NebulaModelType.EDGE_TYPE

    @classmethod
    def _construct(cls):
        pass
