FROM python:3.9-slim

RUN mkdir app

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
RUN pip install poetry

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

# ENV PATH="${PATH}:/root/.poetry/bin"
# ENV PYTHONPATH=.

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --without dev --no-root

# for migrations
# COPY migrations .
# COPY aerich.ini .

COPY src/ .
