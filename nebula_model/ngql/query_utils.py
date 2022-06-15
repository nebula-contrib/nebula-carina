import copy

from nebula_model.utils import tree


class Q(tree.Node):
    """
    Encapsulate filters as objects that can then be combined logically (using
    `&` and `|`).
    """
    # Connection types
    AND = 'AND'
    OR = 'OR'
    default = AND
    conditional = True

    def __init__(self, *args, _connector=None, _negated=False, **kwargs):
        super().__init__(children=[*args, *sorted(kwargs.items())], connector=_connector, negated=_negated)

    def _combine(self, other, conn):
        if not isinstance(other, Q):
            raise TypeError(other)

        # If the other Q() is empty, ignore it and just use `self`.
        if not other:
            return copy.deepcopy(self)
        # Or if this Q is empty, ignore it and just use `other`.
        elif not self:
            return copy.deepcopy(other)

        obj = type(self)()
        obj.connector = conn
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = type(self)()
        obj.add(self, self.AND)
        obj.negate()
        return obj

    def resolve_expression(self, ):
        # TODO
        return
