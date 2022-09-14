from typing import Type, Iterable
from nebula_carina.models.abstract import NebulaConvertableProtocol
from nebula_carina.ngql.query.conditions import Condition
from nebula_carina.ngql.query.match import match, OrderBy, Limit


class SingleMatchResult(object):

    def __init__(self, result: dict[str, NebulaConvertableProtocol]):
        self.__data = result

    def dict(self):
        return {k: v.dict() for k, v in self.__data.items()}

    def __getitem__(self, item):
        return self.__data[item]

    def __iter__(self):
        for key, value in self.__data.items():
            yield key, value


class ModelBuilder(object):
    @staticmethod
    def match(
            pattern: str, to_model_dict: dict[str, Type[NebulaConvertableProtocol]],
            *, distinct_field: str = None,
            condition: Condition = None, order_by: OrderBy = None, limit: Limit = None
    ) -> Iterable[SingleMatchResult]:  # should be model
        output = ', '.join(
            ("DISTINCT " if key == distinct_field else "") + key
            for key in to_model_dict.keys()
        )
        results = match(pattern, output, condition, order_by, limit)
        return (
            SingleMatchResult({
                key: to_model_dict[key].from_nebula_db_cls(value.value)
                for key, value in zip(results.keys(), row.values) if key in to_model_dict
            }) for row in results.rows()
        )

    @staticmethod
    def serialized_match(*args, **kwargs):
        return [res.dict() for res in ModelBuilder.match(*args, **kwargs)]
