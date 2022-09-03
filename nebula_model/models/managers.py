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
    def get(self, vid: str | int):
        try:
            return list(
                ModelBuilder.match(
                    f'(v{self.model.get_tag_db_names_pattern()})', {'v': self.model},
                    condition=RawCondition(f"id(v) == {vid2str(vid)}"),
                    limit=Limit(1)
                )
            )[0]['v']
        except IndexError:
            raise VertexDoesNotExistError(vid)

    def delete(self, vid_list: list[str, int], with_edge: bool = True):
        return run_ngql(delete_vertex_ngql(vid_list, with_edge))


class BaseEdgeManager(Manager):
    def find_between(self, src_vid: str | int, dst_vid: str | int, edge_type=None):
        # edge_type: EdgeModel | None
        return [
            r['e'] for r in ModelBuilder.match(
                    f'(v1)-[e{(":" + edge_type.db_name()) if edge_type else ""}]->(v2)', {'e': self.model},
                    condition=RawCondition(
                        f"id(v1) == {vid2str(src_vid)} AND id(v2) == {vid2str(dst_vid)}"
                    )
                )
        ]

    def get(self, src_vid: str | int, dst_vid: str | int, edge_type):
        try:
            return self.find_between(src_vid, dst_vid, edge_type)[0]
        except IndexError:
            raise EdgeDoesNotExistError

    def delete(self, edge_definitions: list[EdgeDefinition]):
        return run_ngql(delete_edge_ngql(self.model.get_edge_type_and_model()[1].db_name(), edge_definitions))
