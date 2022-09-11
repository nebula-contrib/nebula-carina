from abc import ABC


class Statement(ABC):

    __slots__ = ()

    def __str__(self):
        pass

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
               and not any(getattr(self, s, None) != getattr(other, s, None) for s in self.__slots__)
