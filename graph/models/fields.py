from pydantic import Field


class NebulaField(Field):
    pass


class VIDField(NebulaField):
    pass


class NumberField(NebulaField):
    pass


class BoolField(NebulaField):
    pass


class StringField(NebulaField):
    pass


class DateField(NebulaField):
    pass


class DateTimeField(NebulaField):
    pass


class TimeField(NebulaField):
    pass


