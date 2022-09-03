
class DuplicateEdgeTypeNameError(Exception):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return f'Duplicate edge type named {self.name}.'


class VertexDoesNotExistError(Exception):
    def __init__(self, vid):
        super().__init__()
        self.vid = vid

    def __str__(self):
        return f'Vertex matching id: {type(self.vid)} = {self.vid} does not exist.'


class EdgeDoesNotExistError(Exception):
    def __init__(self, src_vid: str | int, dst_vid: str | int):
        super().__init__()
        self.src_vid = src_vid
        self.dst_vid = dst_vid

    def __str__(self):
        return f'Edge Matching \n' \
               f'src_vid: {type(self.src_vid)} = {self.src_vid} \n' \
               f'dst_vid: {type(self.dst_vid)} = {self.dst_vid} ' \
               f'does not exist.'
