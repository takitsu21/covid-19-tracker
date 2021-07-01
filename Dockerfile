FROM python:3.9-slim

WORKDIR /app
RUN apt-get update

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

COPY . .