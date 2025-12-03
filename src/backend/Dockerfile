FROM python:3.13-slim

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"
ENV UV_PYTHON=/usr/local/bin/python3.13

COPY ./pyproject.toml ./uv.lock /app/
WORKDIR /app

ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync


ENV BACKEND_PORT=8000
EXPOSE 8000/tcp


CMD uv run python \
    -m src.backend.main
