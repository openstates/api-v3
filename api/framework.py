class InvalidSegment(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"invalid segment '{self.name}'"


def segment(f):
    f._is_segment = True
    return f


class ResourceMetaclass(type):
    def __new__(cls, name, bases, dct):
        obj = super().__new__(cls, name, bases, dct)
        obj._segments = {k: v for k, v in dct.items() if hasattr(v, "_is_segment")}
        return obj


class Resource(metaclass=ResourceMetaclass):
    def as_dict(self, segments=None):
        if not segments:
            segments = ["basic"]
        resp = {}
        for segment in segments:
            try:
                segfunc = self._segments[segment]
            except KeyError:
                raise InvalidSegment(segment)
            resp.update(segfunc(self))
        return resp
