FROM antonapetrov/uvicorn-gunicorn-fastapi:python3.9

# install Poetry
RUN pip install --disable-pip-version-check --no-cache-dir -q wheel \
    pip install --disable-pip-version-check --no-cache-dir -q poetry crcmod

ENV MODULE_NAME=api.main
WORKDIR /app

COPY pyproject.toml /app/
COPY poetry.lock /app/
RUN poetry install --no-root --only main
COPY . /app

