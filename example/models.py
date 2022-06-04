from datetime import datetime

from graph.models import models
from graph.models.fields import NebulaField
from graph.ngql import data_types

PREFIX = ''


class Figure(models.TagModel):
    vid: int = NebulaField(data_types.Int64, ..., )
    name: str = NebulaField(data_types.FixedString(40), ..., max_length=40, )
    age: int = NebulaField(data_types.Int8, ..., )
    is_male: bool = NebulaField(data_types.Bool, True)


class Source(models.TagModel):
    vid: int = NebulaField(data_types.Int64, ..., )
    name: str = NebulaField(data_types.FixedString(30), ..., max_length=30, )  # TODO max length


# class Belong(models.EdgeTypeModel):
#     created_on: datetime = NebulaField(..., )
