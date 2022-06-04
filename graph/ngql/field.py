from typing import Any

from graph.ngql import data_types


class NebulaDatabaseField(object):
    __slots__ = ('prop_name', 'data_type', 'nullable', 'default', 'comment')

    def __init__(
            self, prop_name: str, data_type: data_types.DataType,
            nullable: bool = False, default: Any = None, comment: str = None
    ):
        self.prop_name = prop_name
        self.data_type = data_type
        self.nullable = nullable
        self.default = default
        self.comment = comment

    def __eq__(self, other):
        if not isinstance(other, NebulaDatabaseField):
            return False
        return (
            self.prop_name == other.prop_name and self.data_type == other.data_type
            and self.nullable == other.nullable and self.default == other.default and self.comment == other.comment
        )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'{self.prop_name} {self.data_type} {"NULL" if self.nullable else "NOT NULL"}' \
               f'{f" DEFAULT {self.default}" if self.default is not None else ""}' \
               f'{f" COMMENT {self.comment}" if self.comment else ""}'
