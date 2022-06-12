from graph.ngql.connection.connection import run_ngql
from graph.ngql.statements.clauses import OrderBy, Limit


def match(
        pattern: str, output: str, condition: str | None = None,
        order_by: OrderBy | None = None, limit: Limit | None = None
):
    ngql = f'MATCH {pattern}{f" WHERE {condition}" if condition else ""} ' \
           f'RETURN {output}{" " + str(order_by) if order_by else ""}' \
           f'{" " + str(limit) if limit else ""};'
    print(ngql)
    return run_ngql(ngql)
