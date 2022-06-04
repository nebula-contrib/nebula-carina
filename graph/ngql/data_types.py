from enum import Enum


class DataType(object):
    __slots__ = tuple()

    def __str__(self):
        raise NotImplementedError


class NumberType(Enum):
    INT64 = 'INT64'
    INT32 = 'INT32'
    INT16 = 'INT16'
    INT8 = 'INT8'
    FLOAT = 'FLOAT'
    DOUBLE = 'DOUBLE'


class Number(DataType):
    __slots__ = ('number_type', )

    def __init__(self, number_type: NumberType = NumberType.INT64):
        self.number_type = number_type

    def __str__(self):
        return self.number_type.value


class StringType(Enum):
    FIXED_STRING = 'FIXED_STRING'
    STRING = 'STRING'


class String(DataType):
    __slots__ = ('string_type', 'max_length')

    def __init__(self, string_type: StringType = StringType.STRING, max_length=None):
        assert string_type == StringType.STRING or max_length
        self.string_type = string_type
        self.max_length = max_length

    def __str__(self):
        if self.string_type == StringType.STRING:
            return self.string_type.value
        return f'{self.string_type.value}({self.max_length})'


class FixedString(String):
    def __init__(self, max_length):
        super().__init__(StringType.FIXED_STRING, max_length)


class Bool(DataType):
    def __str__(self):
        return 'BOOL'
