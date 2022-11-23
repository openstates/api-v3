FROM antonapetrov/uvicorn-gunicorn-fastapi:python3.9-slim

# install Poetry
RUN pip3 install --disable-pip-version-check --no-cache-dir wheel \
    && pip3 install --disable-pip-version-check --no-cache-dir poetry crcmod

ENV MODULE_NAME=api.main
WORKDIR /app

COPY pyproject.toml /app/
COPY poetry.lock /app/
RUN poetry install --no-root --only main
COPY . /app
