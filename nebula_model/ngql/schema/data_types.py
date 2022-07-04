from abc import ABC
from datetime import datetime, date, time

import pytz

from nebula_model.utils.utils import pascal_case_to_snake_case, read_str
from nebula3.common import ttypes
from nebula_model.settings import database_settings

data_type_factory = {}
ttype2data_type = {}


class DataTypeMetaClass(type):
    def __init__(cls, classname, superclasses, attributedict):
        super().__init__(classname, superclasses, attributedict)
        if cls.__name__ != 'DataType':
            data_type_factory[pascal_case_to_snake_case(cls.__name__).upper()] = cls
            if hasattr(cls, 'nebula_ttype'):
                ttype2data_type[getattr(cls, 'nebula_ttype')] = cls


class DataType(ABC, metaclass=DataTypeMetaClass):
    __slots__ = tuple()

    nebula_ttype = None

    def __str__(self):
        return pascal_case_to_snake_case(self.__class__.__name__).upper()

    def __eq__(self, other):
        return type(self) == type(other)

    @classmethod
    def ttype2python_type(cls, value):
        return read_str(value)

    @classmethod
    def value2db_str(cls, value):
        raise NotImplementedError


class Digit(DataType, ABC):
    @classmethod
    def value2db_str(cls, value):
        if value is None:
            return 'NULL'
        if not str(value).isdigit():
            raise ValueError('%s value should be None or digit' % cls.__name__)
        return str(value)


class Int64(Digit):
    pass


class Int32(Digit):
    pass


class Int16(Digit):
    pass


class Int8(Digit):
    pass


class Float(Digit):
    pass


class Double(Digit):
    pass


class String(DataType):
    @classmethod
    def value2db_str(cls, value):
        if value is None:
            return 'NULL'
        return f'"{value}"'


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

    @classmethod
    def value2db_str(cls, value):
        if value is None:
            return 'NULL'
        return f'"{value}"'


class Bool(DataType):
    @classmethod
    def value2db_str(cls, value):
        if value is None:
            return 'NULL'
        return 'true' if value else 'false'


class Date(DataType):
    nebula_ttype = ttypes.Date
    auto = ''

    @classmethod
    def ttype2python_type(cls, value: ttypes.Date | str):
        if value is None:
            return
        if value == 'date()':
            return ''
        if isinstance(value, ttypes.Date):
            return date(value.year, value.month, value.day)
        raise ValueError('Date value should be None or date')

    @classmethod
    def value2db_str(cls, value: None | str | time):
        if value is None:
            return 'NULL'
        if value == Date.auto:
            return 'date()'
        assert isinstance(value, time), 'Date python value should be None or datetime.date'
        return f'date("{value}")'


class Time(DataType):
    nebula_ttype = ttypes.Time
    auto = ''

    @classmethod
    def ttype2python_type(cls, value: ttypes.Time | str):
        if value is None:
            return
        if value == 'time()':
            return ''
        if isinstance(value, ttypes.Time):
            return time(
                value.hour, value.minute, value.sec, value.microsec,
                tzinfo=pytz.timezone(database_settings.timezone_name)
            )
        raise ValueError('Time value should be None or Time')

    @classmethod
    def value2db_str(cls, value: None | str | time):
        if value is None:
            return 'NULL'
        if value == Time.auto:
            return 'time()'
        assert isinstance(value, time), 'DateTime python value should be None or datetime.time'
        return f'time("{value}")'


class Datetime(DataType):
    nebula_ttype = ttypes.DateTime
    auto = ''

    @classmethod
    def ttype2python_type(cls, value: ttypes.DateTime | str):
        if value is None:
            return
        if value == 'datetime()':
            return ''
        if isinstance(value, ttypes.DateTime):
            return datetime(
                value.year, value.month, value.day, value.hour, value.minute, value.sec, value.microsec,
                tzinfo=pytz.timezone(database_settings.timezone_name)
            )
        raise ValueError('DateTime ngql value should be None or DateTime')

    @classmethod
    def value2db_str(cls, value: None | str | datetime):
        if value is None:
            return 'NULL'
        if value == Datetime.auto:
            return 'datetime()'
        assert isinstance(value, datetime), 'DateTime python value should be None or datetime.datetime'
        return f'datetime("{value}")'


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


def ttype2python_value(val:  any):
    return (ttype2data_type[type(val)] if type(val) in ttype2data_type else DataType).ttype2python_type(val)
