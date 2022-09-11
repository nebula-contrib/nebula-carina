from nebula_carina.ngql.statements.core import Statement


class OrderBy(Statement):
    __slots__ = ('expressions', )

    def __init__(self, expressions: list[str]):
        def make_expr(expr):
            if expr[0] == '-':
                return False, expr[1::]
            return True, expr
        self.expressions = [make_expr(expression) for expression in expressions]

    def __str__(self):
        return f'ORDER BY ' \
               f'{", ".join("%s %s" % (expr, "ASC" if is_asc else "DESC") for is_asc, expr in self.expressions)}'


class Limit(Statement):
    __slots__ = ('limit', 'skip')

    def __init__(self, limit, skip=0):
        self.limit = limit
        self.skip = skip

    def __str__(self):
        return f'{f"SKIP {self.skip} " if self.skip else ""}LIMIT {self.limit}'
