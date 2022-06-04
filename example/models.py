from graph.models import models
from graph.models.fields import create_nebula_field as _
from graph.ngql import data_types


class Figure(models.TagModel):
    vid: int = _(data_types.Int64, ..., )
    name: str = _(data_types.FixedString(30), ..., )
    age: int = _(data_types.Int16, ..., )
    valid_until: int = _(data_types.Int64, None, )
    is_virtual: bool = _(data_types.Bool, True)

    class Meta:
        ttl_duration = 100
        ttl_col = 'valid_until'


class Source(models.TagModel):
    vid: int = _(data_types.Int64, ..., )
    name: str = _(data_types.FixedString(30), ..., )


class Belong(models.EdgeTypeModel):
    pass
