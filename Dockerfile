FROM antonapetrov/uvicorn-gunicorn-fastapi:python3.9-slim

# install Poetry
# also disable virtual environment creation so global installs (like gunicorn)
# can actually see packages
RUN pip3 install --disable-pip-version-check --no-cache-dir wheel \
    && pip3 install --disable-pip-version-check --no-cache-dir poetry crcmod \
    && poetry config virtualenvs.create false

ENV MODULE_NAME=api.main
WORKDIR /app

COPY pyproject.toml /app/
COPY poetry.lock /app/
RUN poetry install --no-root --only main
COPY . /app
