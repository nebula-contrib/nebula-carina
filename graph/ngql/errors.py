class NGqlError(Exception):
    def __init__(self, msg, code):
        self.code = code
        self.msg = msg
        super().__init__()
