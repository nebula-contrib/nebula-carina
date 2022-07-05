from enum import Enum


class Condition(object):
    pass


class RawCondition(Condition):
    def __init__(self, raw_str):
        self.raw_str = raw_str

    def __str__(self):
        return self.raw_str


class ConditionOperator(Enum):
    AND = 'and'
    OR = 'or'
    NOT = 'not'
    XOR = 'xor'


class NodeCondition(Condition):

    def __init__(self, _op: ConditionOperator = ConditionOperator.AND, **kwargs):
        self._op = _op
        for key, val in kwargs:
            pass
