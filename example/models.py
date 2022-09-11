from datetime import datetime
from typing import Optional

from nebula_carina.models import models
from nebula_carina.models.fields import create_nebula_field as _
from nebula_carina.ngql.schema import data_types


class Figure(models.TagModel):
    name: str = _(data_types.FixedString(30), ..., )
    age: int = _(data_types.Int16, ..., )
    valid_until: int = _(data_types.Int64, None, )
    hp: int = _(data_types.Int16, 100, )
    style: str = _(data_types.FixedString(10), 'rap', )
    is_virtual: bool = _(data_types.Bool, True)
    created_on: datetime = _(data_types.Datetime, data_types.Datetime.auto)
    some_dt: datetime = _(data_types.Datetime, datetime(2022, 1, 1))

    class Meta:
        ttl_duration = 100
        ttl_col = 'valid_until'


class Source(models.TagModel):
    name: str = _(data_types.FixedString(30), ..., )


class Belong(models.EdgeTypeModel):
    pass


class Love(models.EdgeTypeModel):
    way: str = _(data_types.FixedString(10), ..., )
    times: int = _(data_types.Int8, ..., )


class Support(models.EdgeTypeModel):
    food_amount: int = _(data_types.Int16, ..., )


class VirtualCharacter(models.VertexModel):
    figure: Figure
    source: Source


class LimitedCharacter(models.VertexModel):
    figure: Figure
