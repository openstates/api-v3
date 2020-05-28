from django.http import JsonResponse
import json


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
    def _call_view(self, dictionary):
        params = {}
        error = None
        for parameter in self.parameters:
            try:
                params[parameter.name] = dictionary[parameter.name]
            except KeyError:
                if parameter.default == Required:
                    error = f"missing required parameter '{parameter.name}'"
                else:
                    params[parameter.name] = parameter.default
        segments = dictionary.get("segments", "basic").split(",")
        results = []
        if not error:
            results = self.get_results(**params, segments=segments)
        data = [self.wrap_resource(r).as_dict(segments) for r in results]
        return {"error": error, "data": data}

    def as_django_view(self):
        def viewfunc(request, *args, **kwargs):
            body = self._call_view(request.GET)
            return JsonResponse(body)
        return viewfunc

    def as_lambda_handler(self):
        def handler(event, context):
            query_string = event.get("queryStringParameters", {})
            body = self._call_view(query_string)
            return {
                "statusCode": 200,
                "body": json.dumps(body),
                "headers": {"Content-Type": "application/json"},
            }
        return handler
