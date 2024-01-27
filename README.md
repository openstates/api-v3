# Open States API v3

This repository contains the code responsible for v3 of the Open States API, currently in beta.

Report API Issues at https://github.com/openstates/issues/

## Links

* [Contributor's Guide](https://docs.openstates.org/en/latest/contributing/getting-started.html)
* [Documentation](https://docs.openstates.org/en/latest/api/v3/)
* [Code of Conduct](https://docs.openstates.org/en/latest/contributing/code-of-conduct.html)

## Multi-arch builds

The selected base image supports `amd64` and `arm64` build targets (and this is shown in the CI workflow).
Use `docker buildx` for local multi-arch builds, e.g.

```bash
docker buildx create --use
docker buildx build --platform amd64,arm64 .
```

## Deploy

See [infrastructure repo](https://github.com/openstates/infrastructure#api-restarts). Plural employees also see the
[Open States Maintenance ops guide](https://civic-eagle.atlassian.net/wiki/spaces/ENG/pages/1393459207/Open+States+Maintenance#%E2%80%9CRestarting%E2%80%9D-the-API)

## Running locally

To run locally, you first need to have a running local
database [following these instructions](https://docs.openstates.org/contributing/local-database/)

You also need to have a redis instance running. That can be run via the docker-compose config included in this package
by running `docker compose up redis`

You can then run the app directly with the command:

```bash
DATABASE_URL=postgresql://openstates:openstates@localhost:5405/openstatesorg poetry run uvicorn api.main:app
```

* Check that the port is correct for your locally running database
* Username/password/dbname in example above are from openstates-scrapers docker-compose.yml, they also need to match the
  local DB.

To test out hitting the API, there will need to be a user account + profile entry with an API key in the local DB. The
scripts involved in the above-mentioned instructions (openstates.org repo init DB) should result in the creation of an
API key called `testkey` that can be used for local testing.

## Architecture

Components of this FastAPI application:

* Routes, found in the `api/` folder, such as `api/bills.py`. These expose HTTP API routes and contain the business
  logic executed when a request hits that route.
* SQL Alchemy models, found in the `api/db/models` folder, such as `api/db/models/bills.py` that define the data models
  used by business logic to query data.
* Pydantic schemas, found in the `api/schemas.py` folder, which define how data from the database is transformed into
  output that is returned by business logic to the client.
* Pagination logic, found in `api/pagination.py` and in route files, provides a semi-magic way for business logic to
  use SQL Alchemy models to manage things like includes, pagination of results, etc..

If you want to make a change, such as adding a related entity to output on an endpoint, you likely need to make changes
to:

* The Model file: add the new entity as a model, and a relationship property on the entity that is related to it. This
  informs which columns are selected via which join logic.
* The Pydantic schema: add the entity and fields to the output schema. Even if the Model changes are correct, the data
  will not show up in API output unless it is in the schema.
* The relevant Pagination object in the route file: you may need to add to `include_map_overrides` to tell the
  pagination system that sub-entities should be fetched when an include is requested.