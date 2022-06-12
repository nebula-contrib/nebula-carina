import json

from graph.ngql.statements.core import Statement


class EdgeDefinition(Statement):
    __slots__ = ('src_vid', 'dst_vid', 'rank')

    def __init__(self, src_vid: str | int, dst_vid: str | int, rank: int = 0):
        self.src_vid = json.dumps(src_vid)
        self.dst_vid = json.dumps(dst_vid)
        self.rank = rank

    def __str__(self):
        return f'{self.src_vid} -> {self.dst_vid}@{self.rank}'


class EdgeValue(Statement):
    __slots__ = ('edge_direction', 'prop_values')

    def __init__(self, src_vid: str | int, dst_vid: str | int, prop_values: list[any], rank: int = 0):
        self.edge_direction = EdgeDefinition(src_vid, dst_vid, rank)
        self.prop_values = [json.dumps(v) for v in prop_values]

    def __str__(self):
        return f'{self.edge_direction}: ({", ".join(self.prop_values)})'
