from typing import Union, Any, Optional, TYPE_CHECKING, Type, Callable

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from nebula_carina.ngql.schema.data_types import DataType, FixedString
from nebula_carina.ngql.statements.schema import SchemaField


if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny

NoArgAnyCallable = Callable[[], Any]

class NebulaFieldInfo(FieldInfo):
    """
    field info overwrite pydantic field info
    """
    __slots__ = ('data_type', )

    def __init__(self, data_type: Union[DataType, Type[DataType]],  **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.data_type = data_type if isinstance(data_type, DataType) else data_type()

    def create_db_field(self, field_name) -> SchemaField:
        return SchemaField(
            field_name, self.data_type, nullable=self.default is None,
            default=self.default if self.default is not Ellipsis else None, comment=self.description
        )


def create_nebula_field(
        data_type: Union[DataType, Type[DataType]],
        default: Any = None,
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
    if isinstance(data_type, FixedString) and not max_length:
        max_length = data_type.max_length
    field_info = NebulaFieldInfo(
        data_type,
        default=default,
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
    return field_info
