class NGqlError(Exception):
    def __init__(self, msg, code):
        self.code = code
        self.msg = msg
        super().__init__()

    def __str__(self):
        return f'ERROR CODE: {self.code}\n{self.msg}'
