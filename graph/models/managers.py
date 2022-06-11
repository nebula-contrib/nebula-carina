import json
from abc import ABC

from graph.models.errors import RecordDoesNotExistError
from graph.ngql.connection import run_ngql
from graph.ngql.query import Limit, OrderBy
from graph.models.model_builder import ModelBuilder
from graph.ngql.vertex import delete_vertex_ngql


class Manager(ABC):
    def __init__(self):
        self.model = None

    def register(self, model):
        self.model = model


class BaseVertexManager(Manager):
    def any(self, limit: Limit = Limit(10), order_by: OrderBy = None):
        return [
            item['v'] for item in ModelBuilder.match('(v)', {'v': self.model}, order_by=order_by, limit=limit)
        ]

    def get(self, vid: str | int):
        try:
            return list(
                ModelBuilder.match('(v)', {'v': self.model}, condition=f"id(v) == {json.dumps(vid)}", limit=Limit(1))
            )[0]['v']
        except IndexError:
            raise RecordDoesNotExistError(vid)

    def delete(self, vid_list: list[str, int], with_edge: bool = True):
        return run_ngql(delete_vertex_ngql(vid_list, with_edge))
