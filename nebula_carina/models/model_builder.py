from typing import Iterable, Type
from nebula_carina.models.abstract import NebulaAdaptor
from nebula_carina.ngql.query.conditions import Condition
from nebula_carina.ngql.query.match import match, OrderBy, Limit


class ModelBuilder(object):
    @staticmethod
    def match(
            pattern: str, to_model_dict: dict[str, Type[NebulaAdaptor]],  # should be model
            *, distinct_field: str = None,
            condition: Condition = None, order_by: OrderBy = None, limit: Limit = None
    ) -> Iterable[dict[str, NebulaAdaptor]]:  # should be model
        output = ', '.join(
            ("DISTINCT " if key == distinct_field else "") + key
            for key in to_model_dict.keys()
        )
        results = match(pattern, output, condition, order_by, limit)
        return (
            {
                key: to_model_dict[key].from_nebula_db_cls(value.value)
                for key, value in zip(results.keys(), row.values) if key in to_model_dict
            } for row in results.rows()
        )
