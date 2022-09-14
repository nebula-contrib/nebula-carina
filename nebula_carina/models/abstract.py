from abc import ABC

from nebula3.common.ttypes import Vertex, Edge


class NebulaConvertableProtocol(ABC):
    @classmethod
    def from_nebula_db_cls(cls, raw_db_item: Vertex | Edge):
        pass

    def dict(self, *args, **kwargs):
        # this method will be overridden by pydantic
        raise NotImplementedError
