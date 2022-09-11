from abc import ABC

from nebula3.common.ttypes import Vertex, Edge


class NebulaAdaptor(ABC):
    @classmethod
    def from_nebula_db_cls(cls, raw_db_item: Vertex | Edge):
        pass
