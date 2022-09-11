class NGqlError(Exception):
    def __init__(self, msg, code, ngql):
        self.code = code
        self.msg = msg
        self.ngql = ngql
        super().__init__()

    def __str__(self):
        return f'ERROR CODE: {self.code} when executing NGQL [{self.ngql}]\n{self.msg}'


class DefaultSpaceNotExistError(Exception):
    def __init__(self, space_name):
        self.space_name = space_name
        super().__init__()

    def __str__(self):
        return f'Default Space {self.space_name} does not exist.'
