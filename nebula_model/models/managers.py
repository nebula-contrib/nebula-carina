from abc import ABC

from nebula_model.models.errors import VertexDoesNotExistError, EdgeDoesNotExistError
from nebula_model.ngql.connection.connection import run_ngql
from nebula_model.ngql.query.conditions import RawCondition
from nebula_model.ngql.query.match import Limit
from nebula_model.models.model_builder import ModelBuilder
from nebula_model.ngql.record.edge import delete_edge_ngql
from nebula_model.ngql.record.vertex import delete_vertex_ngql
from nebula_model.ngql.statements.edge import EdgeDefinition
from nebula_model.utils.utils import vid2str


class Manager(ABC):
    def __init__(self):
        self.model = None

    def register(self, model):
        self.model = model


class BaseVertexManager(Manager):
    # def any(self, limit: Limit = Limit(10), order_by: OrderBy = None):
    #     return [
    #         item['v'] for item in ModelBuilder.match('(v)', {'v': self.model}, order_by=order_by, limit=limit)
    #     ]

    def get(self, vid: str | int):
        try:
            return list(
                ModelBuilder.match(
                    '(v)', {'v': self.model},
                    condition=RawCondition(f"id(v) == {vid2str(vid)}"),
                    limit=Limit(1)
                )
            )[0]['v']
        except IndexError:
            raise VertexDoesNotExistError(vid)

    def delete(self, vid_list: list[str, int], with_edge: bool = True):
        return run_ngql(delete_vertex_ngql(vid_list, with_edge))


class BaseEdgeManager(Manager):
    # def any(self, limit: Limit = Limit(10), order_by: OrderBy = None):
    #     return [
    #         item['e'] for item in ModelBuilder.match('()-[e]->()', {'e': self.model}, order_by=order_by, limit=limit)
    #     ]

    def get(self, edge_definition: EdgeDefinition):
        # FIXME: rank definition is useless for now
        try:
            return list(
                ModelBuilder.match(
                    '(v1)-[e]->(v2)', {'e': self.model},
                    condition=RawCondition(
                        f"id(v1) == {vid2str(edge_definition.src_vid)} AND id(v2) == {vid2str(edge_definition.dst_vid)}"
                    )
                    , limit=Limit(1)
                )
            )[0]['e']
        except IndexError:
            raise EdgeDoesNotExistError(edge_definition)

    def delete(self, edge_definitions: list[EdgeDefinition]):
        return run_ngql(delete_edge_ngql(self.model.get_edge_type_and_model()[1].db_name(), edge_definitions))
