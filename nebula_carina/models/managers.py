from abc import ABC

from nebula_carina.models.errors import VertexDoesNotExistError, EdgeDoesNotExistError
from nebula_carina.ngql.connection.connection import run_ngql
from nebula_carina.ngql.query.conditions import RawCondition
from nebula_carina.ngql.query.match import Limit
from nebula_carina.models.model_builder import ModelBuilder
from nebula_carina.ngql.record.edge import delete_edge_ngql
from nebula_carina.ngql.record.vertex import delete_vertex_ngql
from nebula_carina.ngql.statements.edge import EdgeDefinition
from nebula_carina.utils.utils import vid2str


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
                    f'(v{self.model.get_db_name_pattern()})', {'v': self.model},
                    condition=RawCondition(f"id(v) == {vid2str(vid)}"),
                    limit=Limit(1)
                )
            )[0]['v']
        except IndexError:
            raise VertexDoesNotExistError(vid)

    def delete(self, vid_list: list[str, int], with_edge: bool = True):
        return run_ngql(delete_vertex_ngql(vid_list, with_edge))

    # easy functions
    def find_sources(
            self, dst_vid: str | int, edge_type, *,
            distinct=False, limit: Limit = None
    ):
        if edge_type is None:
            from nebula_carina.models.models import EdgeTypeModel
            edge_type = EdgeTypeModel
        return [
            r['v1'] for r in ModelBuilder.match(
                f'(v1{self.model.get_db_name_pattern()})-[e{edge_type.get_db_name_pattern()}]->(v2)',
                {'v1': self.model},
                distinct_field='v1' if distinct else None,
                condition=RawCondition(
                    f"id(v2) == {vid2str(dst_vid)}"
                ),
                limit=limit
            )
        ]

    def find_destinations(
            self, src_vid: str | int, edge_type, *,
            distinct=False, limit: Limit = None
    ):
        if edge_type is None:
            from nebula_carina.models.models import EdgeTypeModel
            edge_type = EdgeTypeModel
        return [
            r['v2'] for r in ModelBuilder.match(
                f'(v1)-[e{edge_type.get_db_name_pattern()}]->(v2{self.model.get_db_name_pattern()})',
                {'v2': self.model},
                distinct_field='v2' if distinct else None,
                condition=RawCondition(
                    f"id(v1) == {vid2str(src_vid)}"
                ),
                limit=limit
            )
        ]


class BaseEdgeManager(Manager):
    def find_between(
            self, src_vid: str | int, dst_vid: str | int, edge_type=None,
            *,
            limit: Limit = None
    ):
        if edge_type is None:
            from nebula_carina.models.models import EdgeTypeModel
            edge_type = EdgeTypeModel
        return [
            r['e'] for r in ModelBuilder.match(
                    f'(v1)-[e{edge_type.get_db_name_pattern()}]->(v2)', {'e': self.model},
                    condition=RawCondition(
                        f"id(v1) == {vid2str(src_vid)} AND id(v2) == {vid2str(dst_vid)}"
                    ), limit=limit
                )
        ]

    def find_by_source(self, src_vid: str, edge_type=None, *, limit: Limit = None):
        if edge_type is None:
            from nebula_carina.models.models import EdgeTypeModel
            edge_type = EdgeTypeModel
        return [
            r['e'] for r in ModelBuilder.match(
                    f'(v1)-[e{edge_type.get_db_name_pattern()}]->()', {'e': self.model},
                    condition=RawCondition(
                        f"id(v1) == {vid2str(src_vid)}"
                    ), limit=limit
                )
        ]

    def find_by_destination(self, dst_vid: str, edge_type, *, limit: Limit = None):
        if edge_type is None:
            from nebula_carina.models.models import EdgeTypeModel
            edge_type = EdgeTypeModel
        return [
            r['e'] for r in ModelBuilder.match(
                    f'()-[e{edge_type.get_db_name_pattern()}]->(v2)', {'e': self.model},
                    condition=RawCondition(
                        f"id(v2) == {vid2str(dst_vid)}"
                    ), limit=limit
                )
        ]

    def get(self, src_vid: str | int, dst_vid: str | int, edge_type):
        try:
            return self.find_between(src_vid, dst_vid, edge_type)[0]
        except IndexError:
            raise EdgeDoesNotExistError

    def delete(self, edge_definitions: list[EdgeDefinition]):
        return run_ngql(delete_edge_ngql(self.model.get_edge_type_and_model()[1].db_name(), edge_definitions))
