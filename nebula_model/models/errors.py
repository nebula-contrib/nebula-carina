class VertexDoesNotExistError(Exception):
    def __init__(self, vid):
        super().__init__()
        self.vid = vid

    def __str__(self):
        return f'Vertex Matching id: {type(self.vid)} = {self.vid} does not exist.'


class EdgeDoesNotExistError(Exception):
    def __init__(self, edge_definition):
        super().__init__()
        self.edge_definition = edge_definition

    def __str__(self):
        return f'Edge Matching \n' \
               f'src_vid: {type(self.edge_definition.src_vid)} = {self.edge_definition.src_vid} \n' \
               f'dst_vid: {type(self.edge_definition.dst_vid)} = {self.edge_definition.dst_vid} ' \
               f'does not exist.'
