FROM antonapetrov/uvicorn-gunicorn-fastapi:python3.9

# install Poetry
RUN pip3 install --disable-pip-version-check --no-cache-dir wheel \
    && pip3 install --disable-pip-version-check --no-cache-dir poetry crcmod

ENV MODULE_NAME=api.main

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root --no-dev
COPY . /app

