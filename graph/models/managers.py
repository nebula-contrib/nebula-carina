from abc import ABC
from graph.ngql.query import Limit, OrderBy


class Manager(ABC):
    def __init__(self):
        self.model = None

    def register(self, model):
        self.model = model


class BaseManager(Manager):
    def any(self, limit: Limit = Limit(10), order_by: OrderBy = None):
        from graph.models.model_builder import ModelBuilder
        return [
            item['v'] for item in ModelBuilder.match('(v)', {'v': self.model}, order_by=order_by, limit=limit)
        ]
