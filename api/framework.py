from django.http import JsonResponse


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


class Required:
    pass


class Parameter:
    def __init__(self, name, *, default=Required):
        self.name = name
        self.default = default


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


class Endpoint:
    def as_django_view(self):
        def viewfunc(request, *args, **kwargs):
            error = None
            data = None
            params = {}

            for parameter in self.parameters:
                try:
                    params[parameter.name] = request.GET[parameter.name]
                except KeyError:
                    if parameter.default == Required:
                        error = "missing required parameter '{arg_name}'"
                    else:
                        params[parameter.name] = parameter.default

            segments = request.GET.get("segments", "basic").split(",")

            if not error:
                results = self.get_results(**params, segments=segments)
            data = [self.wrap_resource(r).as_dict(segments) for r in results]

            return JsonResponse({"error": error, "data": data})

        return viewfunc
