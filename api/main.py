import os
import sentry_sdk
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from uvicorn.workers import UvicornWorker
from . import jurisdictions, people, bills

if "SENTRY_URL" in os.environ:
    sentry_sdk.init(os.environ["SENTRY_URL"], traces_sample_rate=1.0)

app = FastAPI()
app.include_router(jurisdictions.router)
app.include_router(people.router)
app.include_router(bills.router)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_headers=["*"],
)


@app.get("/")
async def read_typer():
    return RedirectResponse("/docs")


# @app.get("/debug")
# def debug(request: Request):
#     print(request.scope)
#     return {
#         "headers": request.headers,
#         "url": request.url,
#         "scope.type": request.scope["type"],
#         "scope.http_version": request.scope["http_version"],
#         "scope.server": request.scope["server"],
#         "scope.client": request.scope["client"],
#     }


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Open States API v3",
        version="2020.10.30",
        description="""
* [More documentation](https://docs.openstates.org/en/latest/api/v3/index.html)
* [Register for an account](https://openstates.org/accounts/signup/)
""",
        routes=app.routes,
    )
    # if we want to publish divisions.geo we can like this
    # openapi_schema["paths"]["/divisions.geo"] = {
    #     "get": {
    #         "summary": "Divisions Geo",
    #         "operationId": "divisions_geo_get",
    #         "tags": ["divisions"],
    #         "parameters": [
    #             {
    #                 "required": True,
    #                 "schema": {"title": "Latitude", "type": "number"},
    #                 "name": "lat",
    #                 "in": "query",
    #             },
    #             {
    #                 "required": True,
    #                 "schema": {"title": "Longitude", "type": "number"},
    #                 "name": "lng",
    #                 "in": "query",
    #             },
    #         ],
    #         "responses": {
    #             "200": {"description": "Successful Response"},
    #             "content": {
    #                 "application/json": {
    #                     "schema": "#/components/schemas/JurisdictionList"
    #                 }
    #             },
    #         },
    #     }
    # }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# based on suggestion in https://github.com/encode/uvicorn/issues/343 to add proxy_headers
# also need to set environment variable FORWARDED_ALLOW_IPS (can be * in ECS)
class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "asyncio", "http": "h11", "proxy_headers": True}
