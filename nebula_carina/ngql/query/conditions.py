from enum import Enum

from nebula_carina.ngql.schema.data_types import auto_convert_value_to_db_str


class Condition(object):
    pass


class RawCondition(Condition):
    def __init__(self, raw_str):
        self.raw_str = raw_str

    def __str__(self):
        return self.raw_str


class ConditionOperator(Enum):
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    XOR = 'XOR'


class NodeConditionLeaf(Condition):

    OPERATORS = {
        'lte': '<=',
        'gte': '>=',
        'eq': '==',
        'lt': '<',
        'gt': '>',
        'in': 'IN'
    }

    def __init__(self, pattern, value):
        patterns = pattern.split('__')
        if patterns[-1] in self.OPERATORS:
            self.__op = patterns[-1]
            self.patterns = patterns[0:-1]
        else:
            self.__op = 'eq'
            self.patterns = patterns
        self.value = value

    def make_pattern(self):
        pattern = ''
        for p in self.patterns:
            if p == 'id':
                pattern = f'id({pattern})'
            else:
                pattern += '.' + p if pattern else p
        return pattern

    def __str__(self):
        return f"{self.make_pattern()} {self.OPERATORS[self.__op]} {auto_convert_value_to_db_str(self.value)}"


class NodeCondition(Condition):

    @staticmethod
    def __init_by_leaves(op, leaves):
        node = NodeCondition(_op=op)
        node.__leaves = leaves
        return node

    def __init__(self, *, _op: ConditionOperator = ConditionOperator.AND, **kwargs):
        self.__op = _op  # use an op to connect everyone
        self.__leaves = [NodeConditionLeaf(key, val) for key, val in kwargs.items()]

    def __str__(self):
        if self.__op == ConditionOperator.NOT:
            assert len(self.__leaves) == 1
            return f'NOT ({self.__leaves[0].__str__()})'
        return f' {self.__op.value} '.join(f'({leaf.__str__()})' for leaf in self.__leaves)

    def __and__(self, other):
        assert isinstance(other, NodeCondition)
        return self.__init_by_leaves(ConditionOperator.AND, [self, other])

    def __or__(self, other):
        assert isinstance(other, NodeCondition)
        return self.__init_by_leaves(ConditionOperator.OR, [self, other])

    def __xor__(self, other):
        assert isinstance(other, NodeCondition)
        return self.__init_by_leaves(ConditionOperator.XOR, [self, other])

    def __neg__(self):
        return self.__init_by_leaves(ConditionOperator.NOT, [self])


# short names
Q = NodeCondition
