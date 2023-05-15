FROM antonapetrov/uvicorn-gunicorn-fastapi:python3.9-slim

# improve logging performance (don't buffer messages to output)
ENV PYTHONUNBUFFERED=1
# reduce images size
ENV PYTHONDONTWRITEBYTECODE=1
# next two environment files ensure UTF-8 processing works consistently
ENV PYTHONIOENCODING='utf-8'
ENV LANG='C.UTF-8'

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

# the extra delete steps here probably aren't needed, but good to have available
RUN poetry install --no-root --only main \
  && rm -r /root/.cache/pypoetry/cache /root/.cache/pypoetry/artifacts/ \
  && apt-get autoremove -yqq \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY . /app
