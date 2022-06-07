from abc import ABC

from graph.ngql.connection import run_ngql


class Statement(ABC):
    def to_open_cypher(self) -> str:
        pass


class OrderBy(Statement):
    def __init__(self, expressions: list[str]):
        def make_expr(expr):
            if expr[0] == '-':
                return False, expr[1::]
            return True, expr
        self.expressions = [make_expr(expression) for expression in expressions]

    def to_open_cypher(self) -> str:
        return f'ORDER BY ' \
               f'{", ".join("%s %s" % (expr, "ASC" if is_asc else "DESC") for is_asc, expr in self.expressions)}'


class Limit(Statement):
    def __init__(self, limit, skip=0):
        self.limit = limit
        self.skip = skip

    def to_open_cypher(self) -> str:
        return f'{f"SKIP {self.skip} " if self.skip else ""}LIMIT {self.limit}'


def match(
        pattern: str, output: str, condition: str | None = None,
        order_by: OrderBy | None = None, limit: Limit | None = None
):
    ngql = f'MATCH {pattern}{f" WHERE {condition}" if condition else ""} ' \
           f'RETURN {output}{" " + order_by.to_open_cypher() if order_by else ""}' \
           f'{" " + limit.to_open_cypher() if limit else ""};'
    print(ngql)
    return run_ngql(ngql)
