from enum import Enum

from nebula_carina.ngql.schema import data_types
from nebula_carina.ngql.statements.core import Statement


class SchemaField(Statement):
    __slots__ = ('prop_name', 'data_type', 'nullable', 'default', 'comment')

    def __init__(
            self, prop_name: str, data_type: data_types.DataType,
            nullable: bool = False, default: any = None, comment: str = None
    ):
        self.prop_name = prop_name
        self.data_type = data_type
        self.nullable = nullable
        self.default = self.data_type.clean_default(default)
        self.comment = comment

    def __str__(self):
        comment = f' COMMENT "{self.comment}"' if self.comment else ''
        return f'{self.prop_name} {self.data_type} {"NULL" if self.nullable else "NOT NULL"}' \
               f'{f" DEFAULT {self.data_type.value2db_str(self.default)}" if self.default is not None else ""}' \
               f'{comment}'


class AlterType(Enum):
    ADD = 'ADD'
    DROP = 'DROP'
    CHANGE = 'CHANGE'


class SchemaType(Enum):
    TAG = 'TAG'
    EDGE = 'EDGE'


class Ttl(Statement):
    __slots__ = ('ttl_duration', 'ttl_col')

    def __init__(self, ttl_duration: int, ttl_col: str):
        self.ttl_duration = ttl_duration
        self.ttl_col = ttl_col

    def __str__(self):
        ttl_col = f', TTL_COL = "{self.ttl_col}"' if self.ttl_col else ''
        return f'TTL_DURATION = {self.ttl_duration}{ttl_col}'


class Alter(Statement):
    __slots__ = ('alter_definition_type', 'properties', 'prop_names')

    def __init__(
            self, alter_definition_type: AlterType, *,
            properties: list[SchemaField] | None = None, prop_names: list[str] = None
    ):
        self.alter_definition_type = alter_definition_type
        if self.alter_definition_type == AlterType.DROP:
            assert prop_names
            self.prop_names = prop_names
        else:
            assert properties
            self.properties = properties

    def __str__(self):
        if self.alter_definition_type == AlterType.DROP:
            return f'{self.alter_definition_type.value} ({",".join(self.prop_names)})'
        return f'{self.alter_definition_type.value} ({", ".join(str(p) for p in self.properties)})'
