from django.http import JsonResponse
from django.core.paginator import Paginator
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
    default_per_page = 20

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
        per_page = dictionary.get("per_page", self.default_per_page)
        try:
            per_page = int(per_page)
        except ValueError:
            error = f"invalid per_page '{per_page}'"
        page = dictionary.get("page", 1)
        try:
            page = int(page)
        except ValueError:
            error = f"invalid page '{page}'"

        if not error:
            results = self.get_results(**params, segments=segments)
            paginator = Paginator(results, per_page)
            data = [
                self.wrap_resource(r).as_dict(segments) for r in paginator.page(page)
            ]
        else:
            data = []
        return {
            "error": error,
            "data": data,
            "pagination": {
                "per_page": per_page,
                "page": page,
                "num_pages": paginator.num_pages,
                "num_items": paginator.count,
            },
        }

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
