# Open States API v3

This repository contains the code responsible for v3 of the Open States API, currently in beta.

Report API Issues at https://github.com/openstates/issues/

## Links

* [Contributor's Guide](https://docs.openstates.org/en/latest/contributing/getting-started.html)
* [Documentation](https://docs.openstates.org/en/latest/api/v3/)
* [Code of Conduct](https://docs.openstates.org/en/latest/contributing/code-of-conduct.html)

## Running locally

```bash
DATABASE_URL postgres://localhost:5432 poetry run uvicorn api.main:app
```
