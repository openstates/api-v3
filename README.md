# Open States API v3

This repository contains the code responsible for v3 of the Open States API, currently in beta.

Report API Issues at https://github.com/openstates/issues/

## Links

* [Contributor's Guide](https://docs.openstates.org/en/latest/contributing/getting-started.html)
* [Documentation](https://docs.openstates.org/en/latest/api/v3/)
* [Code of Conduct](https://docs.openstates.org/en/latest/contributing/code-of-conduct.html)

## Multi-arch builds

The selected base image supports `amd64` and `arm64` build targets (and this is shown in the CI workflow). Use `docker buildx` for local multi-arch builds, e.g.

```bash
docker buildx create --use
docker buildx build --platform amd64,arm64 .
```
