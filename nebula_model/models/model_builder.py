from typing import Iterable, Type
from nebula_model.models.abstract import NebulaAdaptor
from nebula_model.ngql.query.conditions import Condition
from nebula_model.ngql.query.match import match, OrderBy, Limit


class ModelBuilder(object):
    @staticmethod
    def match(
            pattern: str, to_model_dict: dict[str, Type[NebulaAdaptor]],  # should be model
            *,
            condition: Condition = None, order_by: OrderBy = None, limit: Limit = None
    ) -> Iterable[dict[str, NebulaAdaptor]]:  # should be model
        results = match(pattern, ', '.join(to_model_dict.keys()), condition, order_by, limit)
        return (
            {
                key: to_model_dict[key].from_nebula_db_cls(value.value)
                for key, value in zip(results.keys(), row.values) if key in to_model_dict
            } for row in results.rows()
        )
