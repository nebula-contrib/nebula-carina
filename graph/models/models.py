from enum import Enum

from pydantic import BaseModel


class NebulaModelType(Enum):
    UNDEFINED = 'undefined'
    TAG = 'tag'
    EDGE_TYPE = 'edge_type'


class NebulaModel(BaseModel):
    model_type = NebulaModelType.UNDEFINED


class TagModel(NebulaModel):
    model_type = NebulaModelType.TAG


class EdgeTypeModel(NebulaModel):
    model_type = NebulaModelType.EDGE_TYPE
