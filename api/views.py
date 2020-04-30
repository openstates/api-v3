from django.http import JsonResponse
from functools import wraps
from . import endpoints


class MissingParameter(Exception):
    pass


def api_endpoint(f, required_params=None, optional_params=None):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        required = required_params or []
        optional = optional_params or []
        error = None
        data = None
        args = {}
        for arg_name in required:
            try:
                args[arg_name] = request.GET[arg_name]
            except KeyError:
                error = "missing required parameter '{arg_name}'"
        for arg_name in optional:
            try:
                args[arg_name] = request.GET[arg_name]
            except KeyError:
                pass

        if not error:
            data = f(**args)

        return JsonResponse({"error": error, "data": data})

    return wrapper


legislators = api_endpoint(endpoints.legislators, ["state"], ["chambers", "segments"])
