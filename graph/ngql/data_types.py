from abc import ABC

from graph.utils.utils import pascal_case_to_snake_case

data_type_factory = {}


class DataTypeMetaClass(type):
    def __init__(cls, classname, superclasses, attributedict):
        super().__init__(classname, superclasses, attributedict)
        if cls.__name__ != 'DataType':
            data_type_factory[pascal_case_to_snake_case(cls.__name__).upper()] = cls


class DataType(object, metaclass=DataTypeMetaClass):
    __slots__ = tuple()

    def __str__(self):
        return pascal_case_to_snake_case(self.__class__.__name__).upper()

    def __eq__(self, other):
        return type(self) == type(other)


class Int64(DataType):
    pass


class Int32(DataType):
    pass


class Int16(DataType):
    pass


class Int8(DataType):
    pass


class Float(DataType):
    pass


class Double(DataType):
    pass


class String(DataType):
    pass


class FixedString(DataType):
    __slots__ = ('max_length', )

    def __init__(self, max_length):
        super().__init__()
        self.max_length = int(max_length)

    def __str__(self):
        return f'{super().__str__()}({self.max_length})'

    def __eq__(self, other):
        if not isinstance(other, FixedString):
            return False
        return self.max_length == other.max_length


class Bool(DataType):
    pass


def string_to_data_type(db_type_string: str) -> DataType:
    db_type_string = db_type_string.upper()
    split_string = db_type_string.split('(', 1)
    db_type, additional = None, None
    if len(split_string) == 1:
        db_type = split_string[0]
    else:
        db_type, additional = split_string
        additional = additional[0:-1]
    data_type_class = data_type_factory.get(db_type)
    if not data_type_class:
        raise RuntimeError('Cannot find the data type!')
    if additional:
        return data_type_class(additional)
    return data_type_class()
