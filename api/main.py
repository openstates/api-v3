import os
import sentry_sdk
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from uvicorn.workers import UvicornWorker
from . import jurisdictions, people, bills, committees, events

if "SENTRY_URL" in os.environ:
    sentry_sdk.init(os.environ["SENTRY_URL"], traces_sample_rate=0.05)


app = FastAPI()
app.include_router(jurisdictions.router)
app.include_router(people.router)
app.include_router(bills.router)
app.include_router(committees.router)
app.include_router(events.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
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
        version="2021.11.12",
        description="""
* [More documentation](https://docs.openstates.org/en/latest/api/v3/index.html)
* [Register for an account](https://openstates.org/accounts/signup/)


**We are currently working to restore experimental support for committees & events.**

During this period please note that data is not yet available for all states
and the exact format of the new endpoints may change slightly depending on user feedback.

If you have any issues or questions use our
[GitHub Issues](https://github.com/openstates/issues/issues) to give feedback.
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
