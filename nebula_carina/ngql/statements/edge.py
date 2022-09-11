from nebula_carina.ngql.statements.core import Statement
from nebula_carina.utils.utils import vid2str


class EdgeDefinition(Statement):
    __slots__ = ('src_vid', 'dst_vid', 'ranking')

    def __init__(self, src_vid: str | int, dst_vid: str | int, ranking: int = 0):
        self.src_vid = src_vid
        self.dst_vid = dst_vid
        self.ranking = ranking

    def __str__(self):
        return f'{vid2str(self.src_vid)} -> {vid2str(self.dst_vid)}@{self.ranking}'


class EdgeValue(Statement):
    __slots__ = ('edge_definition', 'prop_values')

    def __init__(self, src_vid: str | int, dst_vid: str | int, prop_values: list[any], ranking: int = 0):
        self.edge_definition = EdgeDefinition(src_vid, dst_vid, ranking)
        self.prop_values = prop_values

    def __str__(self):
        return f'{self.edge_definition}: ({", ".join(self.prop_values)})'
