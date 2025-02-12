FROM python:3.9-buster

RUN mkdir app

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# copy only requirements, to cache them in docker layer
COPY ./requirements-dev.txt /app/requirements-dev.txt

# install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /app/requirements-dev.txt

COPY . /app
