from graph.models import models
from graph.models.fields import create_nebula_field as _
from graph.ngql import data_types

PREFIX = ''


class Figure(models.TagModel):
    vid: int = _(data_types.Int64, ..., )
    name: str = _(data_types.FixedString(40), ..., max_length=40, )
    age: int = _(data_types.Int8, ..., )
    is_male: bool = _(data_types.Bool, True)
    valid_until: int = _(data_types.Int64, None, )

    class Meta:
        ttl_duration = 100
        ttl_col = 'valid_until'


class Source(models.TagModel):
    vid: int = _(data_types.Int64, ..., )
    name: str = _(data_types.FixedString(30), ..., max_length=30, )  # TODO max length


# class Belong(models.EdgeTypeModel):
#     created_on: datetime = NebulaField(..., )
