import json

from graph.ngql.statements.core import Statement


class EdgeValue(Statement):
    __slots__ = ('src_vid', 'dst_vid', 'prop_values', 'rank')

    def __init__(self, src_vid: str | int, dst_vid: str | int, prop_values: list[any], rank: int = 0):
        self.src_vid = json.dumps(src_vid)
        self.dst_vid = json.dumps(dst_vid)
        self.prop_values = [json.dumps(v) for v in prop_values]
        self.rank = rank

    def __str__(self):
        return f'{self.src_vid} -> {self.dst_vid}@{self.rank}: ({", ".join(self.prop_values)})'
