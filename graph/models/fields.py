from functools import partial
from typing import Union, Any, Optional, TYPE_CHECKING

from pydantic.fields import Undefined, FieldInfo
from pydantic.typing import NoArgAnyCallable
if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny


class NebulaFieldInfo(FieldInfo):
    __slots__ = ('field_type', )

    def __init__(self, field_type, default: Any = Undefined, **kwargs: Any) -> None:
        super().__init__(default, **kwargs)
        self.field_type = field_type


def nebula_field(
            field_type,
            default: Any = Undefined,
            *,
            default_factory: Optional[NoArgAnyCallable] = None,
            alias: str = None,
            title: str = None,
            description: str = None,
            exclude: Union['AbstractSetIntStr', 'MappingIntStrAny', Any] = None,
            include: Union['AbstractSetIntStr', 'MappingIntStrAny', Any] = None,
            const: bool = None,
            gt: float = None,
            ge: float = None,
            lt: float = None,
            le: float = None,
            multiple_of: float = None,
            max_digits: int = None,
            decimal_places: int = None,
            min_items: int = None,
            max_items: int = None,
            unique_items: bool = None,
            min_length: int = None,
            max_length: int = None,
            allow_mutation: bool = True,
            regex: str = None,
            discriminator: str = None,
            repr: bool = True,
            **extra: Any,
):
    field_info = NebulaFieldInfo(
        field_type,
        default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        exclude=exclude,
        include=include,
        const=const,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_items=min_items,
        max_items=max_items,
        unique_items=unique_items,
        min_length=min_length,
        max_length=max_length,
        allow_mutation=allow_mutation,
        regex=regex,
        discriminator=discriminator,
        repr=repr,
        **extra,
    )
    field_info._validate()
    return field_info


VIDField = partial(nebula_field, 'vid')


NumberField = partial(nebula_field, 'number')


BoolField = partial(nebula_field, 'bool')


StringField = partial(nebula_field, 'string')


DateField = partial(nebula_field, 'date')


DateTimeField = partial(nebula_field, 'datetime')


TimeField = partial(nebula_field, 'time')

