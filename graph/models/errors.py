class RecordDoesNotExistError(Exception):
    def __init__(self, iid):
        super().__init__()
        self.iid = iid

    def __str__(self):
        return f'Record Matching id: {type(self.iid)} = {self.iid} dos not exist.'
