
class Condition(object):
    pass


class RawCondition(Condition):
    def __init__(self, raw_str):
        self.raw_str = raw_str

    def __str__(self):
        return self.raw_str
