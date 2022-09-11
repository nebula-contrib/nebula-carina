from nebula3.data.ResultSet import ResultSet

from nebula_carina.ngql.connection.connection import run_ngql
from nebula_carina.ngql.query.conditions import Condition
from nebula_carina.ngql.statements.clauses import OrderBy, Limit


def match(
        pattern: str, output: str, condition: Condition | None = None,
        order_by: OrderBy | None = None, limit: Limit | None = None
) -> ResultSet:
    ngql = f'MATCH {pattern}{f" WHERE {condition}" if condition else ""} ' \
           f'RETURN {output}{" " + str(order_by) if order_by else ""}' \
           f'{" " + str(limit) if limit else ""};'
    return run_ngql(ngql)
